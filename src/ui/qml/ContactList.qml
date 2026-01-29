import QtQuick 2.15              // 基础组件
import QtQuick.Controls 2.15     // 按钮、列表等标准控件
import QtQuick.Layouts 1.15      // 自动布局
import QtGraphicalEffects 1.15   // 阴影、模糊等图形特效

// 联系人列表组件：显示所有的对话（私聊和群聊），并提供搜索和创建群组功能
Rectangle {
    Layout.fillHeight: true             // 垂直方向填满父容器
    Layout.preferredWidth: Theme.contactListWidth // 使用主题定义的列表宽度
    color: Theme.sidebarBg              // 背景颜色
    border.color: Theme.borderLight     // 边框颜色

    // 定义外部可绑定的属性
    property var onlineUsers: []        // 私聊用户数据列表
    property var groupList: []           // 群组数据列表
    property var onUserSelected: function(userId) {}   // 选中用户时的回调
    property var onGroupSelected: function(groupId) {} // 选中群组时的回调
    property var onCreateGroup: function() {}           // 点击创建群组按钮的回调

    ColumnLayout {
        anchors.fill: parent            // 填充整个矩形
        spacing: 0                      // 组件间距为 0

        // 标题栏：显示 "Messages" 字样
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "transparent"        // 透明背景

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

        // 搜索栏区域：包含搜索框和 "+" 创建按钮
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Theme.spacingLarge
            spacing: Theme.spacingMedium

            // 模拟搜索框
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

            // 创建群组按钮：圆形 "+" 按钮
            Button {
                Layout.preferredWidth: Theme.searchBoxHeight
                Layout.preferredHeight: Theme.searchBoxHeight
                hoverEnabled: true

                contentItem: Text {
                    text: "+"
                    // 悬停时文字变白，否则为主色调
                    color: parent.hovered ? Theme.textWhite : Theme.primary
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                background: Rectangle {
                    radius: Theme.searchBoxHeight / 2  // 设置为高度一半，确保是正圆
                    // 悬停时背景变为主色调
                    color: parent.hovered ? Theme.primary : Theme.bgWhite
                    border.color: Theme.borderGray
                    border.width: 1
                    
                    // 为按钮添加轻微的阴影效果
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

                onClicked: onCreateGroup() // 触发创建群组信号
            }
        }

        // 核心组件：统一聊天列表（群组和私聊混合排列）
        ListView {
            id: chatListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true                  // 裁剪超出边界的内容
            spacing: Theme.spacingSmall

            // 动态模型：将群组列表和在线用户列表合并为一个数组
            model: {
                var combinedList = []
                
                // 1. 将群组数据处理并加入列表
                for (var i = 0; i < groupList.length; i++) {
                    combinedList.push({
                        type: 'group',
                        id: groupList[i].group_id,
                        name: groupList[i].group_name,
                        member_count: groupList[i].member_count,
                        is_current: groupList[i].is_current
                    })
                }
                
                // 2. 将私聊用户数据处理并加入列表
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

            // 定义每一项的渲染方式
            delegate: ItemDelegate {
                width: chatListView.width
                height: Theme.userItemHeight
                hoverEnabled: true

                // 每一项的背景样式
                background: Rectangle {
                    // 如果是当前选中的会话，背景变白；悬停时变浅灰
                    color: modelData.is_current ? Theme.bgWhite : (parent.hovered ? "#f5f5f5" : Theme.bgTransparent)
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall // 留出一点边距
                    radius: Theme.radiusXLarge
                    // 选中项显示特定边框色
                    border.color: modelData.is_current ? Theme.borderActive : Theme.bgTransparent
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                // 点击逻辑：判断是群聊还是私聊，调用对应回调
                onClicked: {
                    if (modelData.type === 'group') {
                        onGroupSelected(modelData.id)
                    } else {
                        onUserSelected(modelData.id)
                    }
                }

                // 每一项的具体内容布局
                contentItem: RowLayout {
                    spacing: 12

                    // 左侧头像区域
                    Rectangle {
                        width: Theme.avatarLarge
                        height: Theme.avatarLarge
                        radius: Theme.radiusLarge
                        // 群组用主色调背景，普通用户用浅色背景
                        color: modelData.type === 'group' ? Theme.primary : Theme.bgAvatar
                        opacity: modelData.type === 'group' ? 0.8 : 1.0

                        Text {
                            anchors.centerIn: parent
                            text: modelData.name.charAt(0) // 显示首字母
                            font.bold: true
                            color: modelData.type === 'group' ? Theme.textWhite : Theme.textPrimary
                            font.pixelSize: modelData.type === 'group' ? Theme.fontSizeLarge : Theme.fontSizeNormal
                        }

                        // 头像右下角的状态小指示器
                        Rectangle {
                            width: Theme.iconSizeSmall
                            height: Theme.iconSizeSmall
                            radius: Theme.radiusSmall
                            color: {
                                if (modelData.type === 'group') {
                                    return "#10b981"  // 群组始终显示绿色指示
                                }
                                // 私聊根据 online/offline 切换颜色
                                return modelData.status === "online" ? Theme.online : Theme.offline
                            }
                            border.color: Theme.textWhite
                            border.width: Theme.borderWidthMedium
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom

                            Text {
                                anchors.centerIn: parent
                                text: modelData.type === 'group' ? "👥" : ""  // 群组显示群组小图标
                                font.pixelSize: 8
                                visible: modelData.type === 'group'
                            }
                        }
                    }

                    // 中间名称和二级信息（状态或成员数）
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: modelData.name
                            font.bold: true
                            font.pixelSize: Theme.fontSizeNormal
                            // 离线时名称变浅灰
                            color: {
                                if (modelData.type === 'group') {
                                    return Theme.textPrimary
                                }
                                return modelData.status === "online" ? Theme.textPrimary : Theme.textSecondary
                            }
                        }

                        Label {
                            // 群聊显示成员数，私聊显示在线状态描述
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

                    // 右侧未读消息红色气泡（仅针对有未读消息的私聊显示）
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
