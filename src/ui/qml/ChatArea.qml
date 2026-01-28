import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// 聊天区域组件（包含聊天头部、消息列表和输入框）
Rectangle {
    color: Theme.bgWhite

    property var messageModel
    property var onlineUsers: []
    property string currentChatUserStatus: "offline"
    property var fontAwesomeFamily: ""
    property var onSendMessage: function(text) {}
    property bool isGroupChat: false  // 新增：是否为群聊
    property string groupName: ""      // 新增：群组名称
    property int groupMemberCount: 0  // 新增：群成员数

    // 提供外部调用的滚动方法
    function scrollToBottom() {
        Qt.callLater(function() {
            chatList.forceLayout()
            chatList.positionViewAtEnd()
        })
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 聊天头部
        Rectangle {
            Layout.fillWidth: true
            height: Theme.headerHeight
            color: Theme.bgWhite
            border.color: Theme.borderLight

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingXXLarge
                anchors.rightMargin: Theme.spacingXXLarge
                z: 2

                // 当前聊天用户信息
                ColumnLayout {
                    spacing: 2

                    Label {
                        text: {
                            if (isGroupChat) {
                                return groupName || "Group Chat"
                            }
                            for (var i = 0; i < onlineUsers.length; i++)
                                if (onlineUsers[i].is_current) return onlineUsers[i].username;
                            return "Select a contact";
                        }
                        font.pixelSize: Theme.fontSizeLarge
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    RowLayout {
                        visible: isGroupChat || currentChatUserStatus === "online"
                        
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: isGroupChat ? "#10b981" : Theme.online
                        }

                        Label {
                            text: isGroupChat ? (groupMemberCount + " members") : "Online"
                            font.pixelSize: Theme.fontSizeMedium
                            color: isGroupChat ? "#10b981" : Theme.online
                            font.bold: true
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // 功能按钮（电话、视频、更多）
                RowLayout {
                    spacing: Theme.spacingXLarge
                    z: 3

                    // 电话按钮
                    Text {
                        text: Theme.iconPhone
                        font.family: fontAwesomeFamily
                        font.pixelSize: Theme.iconSizeMedium
                        color: phoneMouseArea.containsMouse ? Theme.primary : Theme.textSecondary
                        scale: phoneMouseArea.containsMouse ? 1.1 : 1.0
                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        MouseArea {
                            id: phoneMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    // 视频按钮
                    Text {
                        text: Theme.iconVideo
                        font.family: fontAwesomeFamily
                        font.pixelSize: Theme.iconSizeMedium
                        color: videoMouseArea.containsMouse ? Theme.primary : Theme.textSecondary
                        scale: videoMouseArea.containsMouse ? 1.1 : 1.0
                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        MouseArea {
                            id: videoMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    // 更多按钮
                    Text {
                        text: Theme.iconMore
                        font.family: fontAwesomeFamily
                        font.pixelSize: Theme.iconSizeMedium
                        color: moreMouseArea.containsMouse ? Theme.primary : Theme.textSecondary
                        scale: moreMouseArea.containsMouse ? 1.1 : 1.0
                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        MouseArea {
                            id: moreMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }
            }
        }

        // 消息列表
        ListView {
            id: chatList
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: messageModel
            clip: true
            spacing: Theme.spacingLarge
            topMargin: Theme.spacingXLarge
            bottomMargin: Theme.spacingXLarge
            leftMargin: Theme.spacingXLarge
            rightMargin: Theme.spacingXLarge

            // 监听消息数量变化，强制刷新布局
            onCountChanged: {
                Qt.callLater(function() {
                    chatList.forceLayout()
                    chatList.positionViewAtEnd()
                })
            }

            delegate: ColumnLayout {
                width: chatList.width - 40
                spacing: Theme.spacingSmall

                RowLayout {
                    Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                    layoutDirection: is_mine ? Qt.RightToLeft : Qt.LeftToRight
                    spacing: 10

                    // 对方头像
                    Rectangle {
                        visible: !is_mine
                        width: Theme.avatarSmall
                        height: Theme.avatarSmall
                        radius: Theme.radiusMedium
                        color: Theme.bgAvatar

                        Text {
                            anchors.centerIn: parent
                            text: from_username.charAt(0)
                            font.pixelSize: 12
                        }
                    }

                    // 消息气泡
                    Rectangle {
                        Layout.maximumWidth: chatList.width * 0.6
                        width: msgText.implicitWidth + 30
                        height: msgText.implicitHeight + 24
                        radius: Theme.radiusBubble
                        color: is_mine ? Theme.primary : Theme.receivedBubble
                        border.color: is_mine ? Theme.primary : Theme.borderLight

                        Text {
                            id: msgText
                            text: content
                            anchors.centerIn: parent
                            color: is_mine ? Theme.textWhite : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeNormal
                            wrapMode: Text.Wrap
                            width: parent.width - 30
                        }
                    }
                }

                // 时间戳
                Label {
                    Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                    text: Qt.formatDateTime(new Date(timestamp * 1000), "hh:mm")
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                }
            }
        }

        // 输入区域
        Rectangle {
            Layout.fillWidth: true
            height: Theme.inputAreaHeight
            color: Theme.bgWhite

            Rectangle {
                anchors.fill: parent
                anchors.margins: Theme.spacingLarge
                radius: Theme.radiusXLarge
                color: Theme.bgInputArea
                border.color: Theme.bgAvatar

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingLarge
                    anchors.rightMargin: 8

                    // 消息输入框
                    TextField {
                        id: messageInput
                        Layout.fillWidth: true
                        placeholderText: {
                            if (isGroupChat) {
                                return "Write a message to group..."
                            }
                            return currentChatUserStatus === "online" ? "Write a message..." : "User is offline"
                        }
                        enabled: isGroupChat || currentChatUserStatus === "online"
                        background: Item {}
                        color: Theme.textPrimary
                        font.pixelSize: Theme.fontSizeNormal
                        onAccepted: sendBtn.clicked()
                    }

                    // 发送按钮
                    Button {
                        id: sendBtn
                        Layout.preferredWidth: Theme.buttonSmall
                        Layout.preferredHeight: Theme.buttonSmall
                        enabled: (isGroupChat || currentChatUserStatus === "online") && messageInput.text.trim().length > 0
                        scale: hovered ? 1.05 : 1.0
                        hoverEnabled: true
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        contentItem: Text {
                            text: Theme.iconSend
                            color: Theme.textWhite
                            font.family: fontAwesomeFamily
                            font.pixelSize: Theme.iconSizeMedium
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: Theme.radiusMedium
                            color: parent.enabled ? (parent.hovered ? "#2563eb" : Theme.primary) : Theme.offline
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        onClicked: {
                            onSendMessage(messageInput.text)
                            messageInput.clear()
                        }
                    }
                }
            }
        }
    }
}
