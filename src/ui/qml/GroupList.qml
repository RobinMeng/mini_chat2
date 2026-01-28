import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// 群组列表组件
Rectangle {
    Layout.fillHeight: true
    Layout.preferredWidth: Theme.contactListWidth
    color: Theme.sidebarBg
    border.color: Theme.borderLight

    property var groupList: []
    property var onGroupSelected: function(groupId) {}
    property var onCreateGroup: function() {}

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 标题和创建按钮
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: "transparent"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingXLarge
                anchors.rightMargin: Theme.spacingXLarge

                Label {
                    text: "Groups"
                    font.pixelSize: Theme.fontSizeTitle
                    font.bold: true
                    color: Theme.textPrimary
                }

                Item { Layout.fillWidth: true }

                // 创建群组按钮
                Button {
                    Layout.preferredWidth: Theme.iconSizeLarge
                    Layout.preferredHeight: Theme.iconSizeLarge
                    hoverEnabled: true

                    contentItem: Text {
                        text: "+"
                        color: Theme.textWhite
                        font.pixelSize: Theme.fontSizeLarge
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                    }

                    background: Rectangle {
                        radius: Theme.radiusMedium
                        color: parent.hovered ? "#2563eb" : Theme.primary
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    onClicked: onCreateGroup()
                }
            }
        }

        // 搜索框
        Rectangle {
            Layout.fillWidth: true
            Layout.margins: Theme.spacingLarge
            height: Theme.searchBoxHeight
            radius: Theme.radiusMedium
            color: Theme.bgWhite
            border.color: Theme.borderGray
            
            Text {
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacingMedium
                anchors.verticalCenter: parent.verticalCenter
                text: "Search groups..."
                color: Theme.textPlaceholder
            }
        }

        // 群组列表
        ListView {
            id: groupListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: groupList
            clip: true
            spacing: Theme.spacingSmall

            delegate: ItemDelegate {
                width: groupListView.width
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

                onClicked: onGroupSelected(modelData.group_id)

                contentItem: RowLayout {
                    spacing: 12

                    // 群组头像
                    Rectangle {
                        width: Theme.avatarLarge
                        height: Theme.avatarLarge
                        radius: Theme.radiusLarge
                        color: Theme.primary
                        opacity: 0.8

                        Text {
                            anchors.centerIn: parent
                            text: modelData.group_name.charAt(0)
                            font.bold: true
                            color: Theme.textWhite
                            font.pixelSize: Theme.fontSizeLarge
                        }

                        // 群组标识
                        Rectangle {
                            width: Theme.iconSizeSmall
                            height: Theme.iconSizeSmall
                            radius: Theme.radiusSmall
                            color: "#10b981"
                            border.color: Theme.textWhite
                            border.width: Theme.borderWidthMedium
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom

                            Text {
                                anchors.centerIn: parent
                                text: "👥"
                                font.pixelSize: 8
                            }
                        }
                    }

                    // 群组信息
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: modelData.group_name
                            font.bold: true
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textPrimary
                        }

                        Label {
                            text: modelData.member_count + " members"
                            font.pixelSize: Theme.fontSizeMedium
                            color: Theme.textSecondary
                        }
                    }

                    // 未读消息数量（预留）
                    Rectangle {
                        visible: false
                        width: Theme.iconSizeLarge
                        height: Theme.iconSizeLarge
                        radius: Theme.radiusMedium
                        color: Theme.unreadBadge

                        Label {
                            anchors.centerIn: parent
                            text: "3"
                            color: Theme.textWhite
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                        }
                    }
                }
            }
        }

        // 空状态提示
        Rectangle {
            visible: groupList.length === 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.spacingLarge

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "👥"
                    font.pixelSize: 48
                }

                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: "No groups yet"
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textSecondary
                }

                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Create a group to start chatting"
                    font.pixelSize: Theme.fontSizeMedium
                    color: Theme.textPlaceholder
                }
            }
        }
    }
}
