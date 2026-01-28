import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

// 联系人列表组件（包含私聊和群聊）
Rectangle {
    Layout.fillHeight: true
    Layout.preferredWidth: Theme.contactListWidth
    color: Theme.sidebarBg
    border.color: Theme.borderLight

    property var onlineUsers: []  // 私聊用户列表
    property var groupList: []     // 群组列表
    property var onUserSelected: function(userId) {}
    property var onGroupSelected: function(groupId) {}
    property var onCreateGroup: function() {}  // 创建群组回调

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 标题栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "transparent"

            Label {
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacingXLarge
                anchors.verticalCenter: parent.verticalCenter
                text: "Messages"
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.textPrimary
            }
        }

        // 搜索框 + 创建群组按钮
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Theme.spacingLarge
            spacing: Theme.spacingMedium

            // 搜索框
            Rectangle {
                Layout.fillWidth: true
                height: Theme.searchBoxHeight
                radius: Theme.radiusMedium
                color: Theme.bgWhite
                border.color: Theme.borderGray
                
                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: Theme.spacingMedium
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Search..."
                    color: Theme.textPlaceholder
                }
            }

            // 创建群组按钮
            Button {
                Layout.preferredWidth: Theme.searchBoxHeight
                Layout.preferredHeight: Theme.searchBoxHeight
                hoverEnabled: true

                contentItem: Text {
                    text: "+"
                    color: parent.hovered ? Theme.textWhite : Theme.primary
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                background: Rectangle {
                    radius: Theme.searchBoxHeight / 2  // 完全圆形
                    color: parent.hovered ? Theme.primary : Theme.bgWhite
                    border.color: Theme.borderGray
                    border.width: 1
                    
                    // 阴影效果
                    layer.enabled: true
                    layer.effect: DropShadow {
                        horizontalOffset: 0
                        verticalOffset: 1
                        radius: 3
                        samples: 7
                        color: "#10000000"
                        spread: 0
                    }
                    
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                onClicked: onCreateGroup()
            }
        }

        // 统一聊天列表（群组 + 私聊）
        ListView {
            id: chatListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacingSmall

            // 合并群组和私聊数据
            model: {
                var combinedList = []
                
                // 添加群组（标记为 type: 'group'）
                for (var i = 0; i < groupList.length; i++) {
                    combinedList.push({
                        type: 'group',
                        id: groupList[i].group_id,
                        name: groupList[i].group_name,
                        member_count: groupList[i].member_count,
                        is_current: groupList[i].is_current
                    })
                }
                
                // 添加私聊用户（标记为 type: 'user'）
                for (var j = 0; j < onlineUsers.length; j++) {
                    combinedList.push({
                        type: 'user',
                        id: onlineUsers[j].user_id,
                        name: onlineUsers[j].username,
                        status: onlineUsers[j].status,
                        unread_count: onlineUsers[j].unread_count,
                        is_current: onlineUsers[j].is_current
                    })
                }
                
                return combinedList
            }

            delegate: ItemDelegate {
                width: chatListView.width
                height: Theme.userItemHeight
                hoverEnabled: true

                background: Rectangle {
                    color: modelData.is_current ? Theme.bgWhite : (parent.hovered ? "#f5f5f5" : Theme.bgTransparent)
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    radius: Theme.radiusXLarge
                    border.color: modelData.is_current ? Theme.borderActive : Theme.bgTransparent
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                onClicked: {
                    if (modelData.type === 'group') {
                        onGroupSelected(modelData.id)
                    } else {
                        onUserSelected(modelData.id)
                    }
                }

                contentItem: RowLayout {
                    spacing: 12

                    // 头像（群组/用户）
                    Rectangle {
                        width: Theme.avatarLarge
                        height: Theme.avatarLarge
                        radius: Theme.radiusLarge
                        color: modelData.type === 'group' ? Theme.primary : Theme.bgAvatar
                        opacity: modelData.type === 'group' ? 0.8 : 1.0

                        Text {
                            anchors.centerIn: parent
                            text: modelData.name.charAt(0)
                            font.bold: true
                            color: modelData.type === 'group' ? Theme.textWhite : Theme.textPrimary
                            font.pixelSize: modelData.type === 'group' ? Theme.fontSizeLarge : Theme.fontSizeNormal
                        }

                        // 状态指示器（群组显示群组图标，私聊显示在线状态）
                        Rectangle {
                            width: Theme.iconSizeSmall
                            height: Theme.iconSizeSmall
                            radius: Theme.radiusSmall
                            color: {
                                if (modelData.type === 'group') {
                                    return "#10b981"  // 群组绿色
                                }
                                return modelData.status === "online" ? Theme.online : Theme.offline
                            }
                            border.color: Theme.textWhite
                            border.width: Theme.borderWidthMedium
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom

                            Text {
                                anchors.centerIn: parent
                                text: modelData.type === 'group' ? "👥" : ""  // 群组显示 emoji
                                font.pixelSize: 8
                                visible: modelData.type === 'group'
                            }
                        }
                    }

                    // 名称和状态信息
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: modelData.name
                            font.bold: true
                            font.pixelSize: Theme.fontSizeNormal
                            color: {
                                if (modelData.type === 'group') {
                                    return Theme.textPrimary
                                }
                                return modelData.status === "online" ? Theme.textPrimary : Theme.textSecondary
                            }
                        }

                        Label {
                            text: {
                                if (modelData.type === 'group') {
                                    return modelData.member_count + " members"
                                }
                                return modelData.status === "online" ? "Active now" : "Offline"
                            }
                            font.pixelSize: Theme.fontSizeMedium
                            color: Theme.textSecondary
                        }
                    }

                    // 未读消息数量（仅私聊显示）
                    Rectangle {
                        visible: modelData.type === 'user' && modelData.unread_count > 0
                        width: Theme.iconSizeLarge
                        height: Theme.iconSizeLarge
                        radius: Theme.radiusMedium
                        color: Theme.unreadBadge

                        Label {
                            anchors.centerIn: parent
                            text: modelData.unread_count
                            color: Theme.textWhite
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                        }
                    }
                }
            }
        }
    }
}
