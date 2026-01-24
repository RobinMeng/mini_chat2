import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

ApplicationWindow {
    id: window
    visible: true
    width: 1000
    height: 700
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "white"

    // 加载 FontAwesome 图标字体
    FontLoader {
        id: fontAwesome
        source: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf"
    }

    readonly property color colPrimary: "#3b82f6"
    readonly property color colCharcoal: "#1a1a1a"
    readonly property color colSidebar: "#f9fafb"
    readonly property color colSentBubble: "#f0f7ff"
    readonly property color colReceivedBubble: "#ffffff"
    readonly property color colOnline: "#10b981"
    readonly property color colOffline: "#94a3b8"

    Connections {
        target: backend
        function onNewMessageReceived(msg) { chatList.positionViewAtEnd() }
        function onNewMessageSent(msg) { chatList.positionViewAtEnd() }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // --- 1. Sidebar ---
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 70
            color: "white"
            border.color: "#f0f0f0"
            DragHandler { onActiveChanged: if (active) window.startSystemMove() }

            ColumnLayout {
                anchors.fill: parent
                anchors.topMargin: 15
                anchors.bottomMargin: 20
                spacing: 25

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 8
                    Rectangle { 
                        width: 12; height: 12; radius: 6; color: "#ff5f56" 
                        MouseArea { anchors.fill: parent; onClicked: window.close(); cursorShape: Qt.PointingHandCursor }
                    }
                    Rectangle { 
                        width: 12; height: 12; radius: 6; color: "#ffbd2e" 
                        MouseArea { anchors.fill: parent; onClicked: window.showMinimized(); cursorShape: Qt.PointingHandCursor }
                    }
                    Rectangle { width: 12; height: 12; radius: 6; color: "#27c93f" }
                }

                Rectangle {
                    Layout.topMargin: 10
                    Layout.alignment: Qt.AlignHCenter
                    width: 40
                    height: 40
                    radius: 12
                    color: colPrimary
                    Text { text: "M"; color: "white"; anchors.centerIn: parent; font.bold: true; font.pixelSize: 20 }
                }

                Repeater {
                    // FontAwesome Unicode: chat(\uf075), group(\uf0c0), folder(\uf07b), settings(\uf013)
                    model: ["\uf075", "\uf0c0", "\uf07b", "\uf013"]
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: 45
                        height: 45
                        radius: 12
                        color: index === 0 ? "#f0f7ff" : "transparent"
                        Text {
                            anchors.centerIn: parent
                            text: modelData
                            font.family: fontAwesome.name
                            font.pixelSize: 18
                            color: index === 0 ? colPrimary : "#94a3b8"
                        }
                    }
                }
                Item { Layout.fillHeight: true }
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 40
                    height: 40
                    radius: 12
                    color: "#e2e8f0"
                    Text { text: backend.currentUserName.charAt(0); anchors.centerIn: parent; font.bold: true }
                }
            }
        }

        // --- 2. Contact List ---
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 280
            color: colSidebar
            border.color: "#f0f0f0"

            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Label { text: "Messages"; font.pixelSize: 20; font.bold: true; padding: 20; color: colCharcoal }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.margins: 15
                    height: 40
                    radius: 10
                    color: "white"
                    border.color: "#e5e7eb"
                    Text { anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: "Search..."; color: "#94a3b8" }
                }
                ListView {
                    id: userListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: backend.onlineUsers
                    clip: true
                    spacing: 5
                    delegate: ItemDelegate {
                        width: userListView.width
                        height: 70
                        background: Rectangle {
                            color: modelData.is_current ? "white" : "transparent"
                            anchors.fill: parent
                            anchors.margins: 5
                            radius: 15
                            border.color: modelData.is_current ? "#e5e7eb" : "transparent"
                        }
                        onClicked: backend.selectUser(modelData.user_id)
                        contentItem: RowLayout {
                            spacing: 12
                            Rectangle {
                                width: 45
                                height: 45
                                radius: 12
                                color: "#e2e8f0"
                                Text { 
                                    anchors.centerIn: parent
                                    text: modelData.username.charAt(0)
                                    font.bold: true 
                                }
                                Rectangle {
                                    width: 12
                                    height: 12
                                    radius: 6
                                    color: modelData.status === "online" ? colOnline : colOffline
                                    border.color: "white"
                                    border.width: 2
                                    anchors.right: parent.right
                                    anchors.bottom: parent.bottom
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Label { 
                                    text: modelData.username
                                    font.bold: true
                                    font.pixelSize: 14
                                    color: modelData.status === "online" ? colCharcoal : "#94a3b8" 
                                }
                                Label { 
                                    text: modelData.status === "online" ? "Active now" : "Offline"
                                    font.pixelSize: 11
                                    color: "#94a3b8" 
                                }
                            }
                            Rectangle {
                                visible: modelData.unread_count > 0
                                width: 20
                                height: 20
                                radius: 10
                                color: "#ff4d4f"
                                Label { 
                                    anchors.centerIn: parent
                                    text: modelData.unread_count
                                    color: "white"
                                    font.pixelSize: 10
                                    font.bold: true 
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- 3. Chat Main ---
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "white"
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Rectangle {
                    Layout.fillWidth: true
                    height: 75
                    color: "white"
                    border.color: "#f0f0f0"
                    DragHandler { onActiveChanged: if (active) window.startSystemMove() }
                    RowLayout {
                        anchors.fill: parent; anchors.leftMargin: 25; anchors.rightMargin: 25
                        ColumnLayout {
                            spacing: 2
                            Label {
                                text: {
                                    for (var i = 0; i < backend.onlineUsers.length; i++) 
                                        if (backend.onlineUsers[i].is_current) return backend.onlineUsers[i].username;
                                    return "Select a contact";
                                }
                                font.pixelSize: 16; font.bold: true; color: colCharcoal
                            }
                            RowLayout {
                                visible: backend.currentChatUserStatus === "online"
                                Rectangle { width: 8; height: 8; radius: 4; color: colOnline }
                                Label { text: "Online"; font.pixelSize: 11; color: colOnline; font.bold: true }
                            }
                        }
                        Item { Layout.fillWidth: true }
                        RowLayout {
                            spacing: 20
                            Text { 
                                text: "\uf095" // phone
                                font.family: fontAwesome.name
                                font.pixelSize: 18
                                color: "#94a3b8" 
                            }
                            Text { 
                                text: "\uf03d" // video-camera
                                font.family: fontAwesome.name
                                font.pixelSize: 18
                                color: "#94a3b8" 
                            }
                            Text { 
                                text: "\uf142" // ellipsis-v
                                font.family: fontAwesome.name
                                font.pixelSize: 18
                                color: "#94a3b8" 
                            }
                        }
                    }
                }
                ListView {
                    id: chatList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: backend.messageModel
                    clip: true
                    spacing: 15
                    topMargin: 20
                    bottomMargin: 20
                    leftMargin: 20
                    rightMargin: 20
                    delegate: ColumnLayout {
                        width: chatList.width - 40
                        spacing: 5
                        RowLayout {
                            Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                            layoutDirection: is_mine ? Qt.RightToLeft : Qt.LeftToRight
                            spacing: 10
                            Rectangle {
                                visible: !is_mine
                                width: 35
                                height: 35
                                radius: 10
                                color: "#e2e8f0"
                                Text { 
                                    anchors.centerIn: parent
                                    text: from_username.charAt(0)
                                    font.pixelSize: 12 
                                }
                            }
                            Rectangle {
                                Layout.maximumWidth: chatList.width * 0.6
                                width: msgText.implicitWidth + 30
                                height: msgText.implicitHeight + 24
                                radius: 18
                                color: is_mine ? colPrimary : colReceivedBubble
                                border.color: is_mine ? colPrimary : "#f0f0f0"
                                Text { 
                                    id: msgText
                                    text: content
                                    anchors.centerIn: parent
                                    color: is_mine ? "white" : colCharcoal
                                    font.pixelSize: 14
                                    wrapMode: Text.Wrap
                                    width: parent.width - 30 
                                }
                            }
                        }
                        Label {
                            Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                            text: Qt.formatDateTime(new Date(timestamp * 1000), "hh:mm")
                            font.pixelSize: 10
                            color: "#94a3b8"
                        }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    height: 90
                    color: "white"
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 15
                        radius: 15
                        color: "#f8fafc"
                        border.color: "#e2e8f0"
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 15
                            anchors.rightMargin: 8
                            TextField {
                                id: messageInput
                                Layout.fillWidth: true
                                placeholderText: backend.currentChatUserStatus === "online" ? "Write a message..." : "User is offline"
                                enabled: backend.currentChatUserStatus === "online"
                                background: Item {}
                                color: colCharcoal
                                font.pixelSize: 14
                                onAccepted: sendBtn.clicked()
                            }
                            Button {
                                id: sendBtn
                                Layout.preferredWidth: 40
                                Layout.preferredHeight: 40
                                enabled: backend.currentChatUserStatus === "online" && messageInput.text.trim().length > 0
                                contentItem: Text { 
                                    text: "\uf1d8" // paper-plane
                                    color: "white"
                                    font.family: fontAwesome.name
                                    font.pixelSize: 18
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter 
                                }
                                background: Rectangle { 
                                    radius: 10
                                    color: parent.enabled ? colPrimary : "#cbd5e1" 
                                }
                                onClicked: { 
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
