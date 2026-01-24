import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    visible: true
    width: 900
    height: 600
    title: "MiniChat - " + backend.currentUserName + " (" + backend.currentUserIp + ")"

    // 主后端对象由 Python 注入
    // 信号连接
    Connections {
        target: backend
        function onChatHistoryChanged(history) {
            messageModel.clear()
            for (var i = 0; i < history.length; i++) {
                messageModel.append(history[i])
            }
            chatList.positionViewAtEnd()
        }
        function onNewMessageReceived(msg) {
            messageModel.append(msg)
            chatList.positionViewAtEnd()
        }
        function onNewMessageSent(msg) {
            messageModel.append(msg)
            chatList.positionViewAtEnd()
        }
    }

    ListModel {
        id: messageModel
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // --- 左侧用户列表 ---
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 250
            color: "#f5f5f5"
            border.color: "#dddddd"

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                Label {
                    text: "在线用户 (" + backend.onlineUsers.length + ")"
                    font.bold: true
                    padding: 10
                    Layout.fillWidth: true
                    background: Rectangle { color: "#e0e0e0" }
                }

                ListView {
                    id: userListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: backend.onlineUsers
                    clip: true
                    delegate: ItemDelegate {
                        width: parent.width
                        highlighted: modelData.is_current
                        onClicked: backend.selectUser(modelData.user_id)

                        contentItem: RowLayout {
                            spacing: 10
                            Rectangle {
                                width: 10; height: 10
                                radius: 5
                                color: "green"
                            }
                            ColumnLayout {
                                Label {
                                    text: modelData.username
                                    font.bold: true
                                }
                                Label {
                                    text: modelData.ip
                                    font.pixelSize: 10
                                    color: "#666666"
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- 右侧聊天区域 ---
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // 聊天标题
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                color: "white"
                border.color: "#dddddd"
                Label {
                    anchors.centerIn: parent
                    text: {
                        for (var i = 0; i < backend.onlineUsers.length; i++) {
                            if (backend.onlineUsers[i].is_current) {
                                return backend.onlineUsers[i].username;
                            }
                        }
                        return "请选择联系人开始聊天";
                    }
                    font.pixelSize: 16
                    font.bold: true
                }
            }

            // 消息显示区
            ListView {
                id: chatList
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: messageModel
                clip: true
                spacing: 10
                footer: Item { height: 10 }
                header: Item { height: 10 }

                delegate: Column {
                    width: chatList.width
                    spacing: 5
                    
                    // 简化判断：直接对比发送者名称和当前用户名
                    property bool isMine: model.from_username === backend.currentUserName
                    Row {
                        anchors.right: isMine ? parent.right : undefined
                        anchors.left: isMine ? undefined : parent.left
                        anchors.rightMargin: 10
                        anchors.leftMargin: 10
                        
                        Rectangle {
                            width: msgLabel.implicitWidth + 20
                            height: msgLabel.implicitHeight + 20
                            radius: 10
                            color: model.from_username === backend.currentUserName ? "#95ec69" : "#ffffff"
                            border.color: "#dddddd"
                            Label {
                                id: msgLabel
                                anchors.centerIn: parent
                                text: model.content
                                wrapMode: Label.Wrap
                                width: Math.min(implicitWidth, chatList.width * 0.6)
                            }
                        }
                    }
                }
            }

            // 输入区
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                color: "#f9f9f9"
                border.color: "#dddddd"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 5
                    
                    TextArea {
                        id: messageInput
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        placeholderText: "输入消息 (Ctrl+Enter 发送)..."
                        wrapMode: TextArea.Wrap
                        Keys.onPressed: {
                            if (event.key === Qt.Key_Return && event.modifiers & Qt.ControlModifier) {
                                sendBtn.clicked()
                                event.accepted = true
                            }
                        }
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        Button {
                            text: "发送文件"
                            onClicked: console.log("文件传输开发中...")
                        }
                        Button {
                            id: sendBtn
                            text: "发送"
                            highlighted: true
                            onClicked: {
                                if (messageInput.text.trim()) {
                                    backend.sendMessage(messageInput.text)
                                    messageInput.clear()
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    onClosing: backend.stop()
}
