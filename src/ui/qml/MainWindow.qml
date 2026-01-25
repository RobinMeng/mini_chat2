import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

ApplicationWindow {
    id: window
    visible: true
    width: Theme.windowWidth
    height: Theme.windowHeight
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"
    
    // 确保窗口背景完全透明（关键：支持圆角）
    background: Rectangle {
        color: "transparent"
        radius: Theme.radiusWindow
    }

    // 加载 FontAwesome 图标字体
    FontLoader {
        id: fontAwesome
        source: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf"
    }

    Connections {
        target: backend
        function onNewMessageReceived(msg) { 
            // 延迟滚动，确保 ListView 渲染完成
            Qt.callLater(function() {
                chatList.positionViewAtEnd()
            })
        }
        function onNewMessageSent(msg) { 
            // 延迟滚动，确保 ListView 渲染完成
            Qt.callLater(function() {
                chatList.positionViewAtEnd()
            })
        }
    }

    // 主容器（圆角窗口）
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        anchors.margins: 0
        radius: Theme.radiusWindow
        color: Theme.bgWhite
        clip: true
        antialiasing: true
        smooth: true
        
        // 使用 layer 来确保圆角正确渲染
        layer.enabled: true
        layer.smooth: true
        layer.effect: OpacityMask {
            maskSource: Rectangle {
                width: mainContainer.width
                height: mainContainer.height
                radius: Theme.radiusWindow
                antialiasing: true
            }
        }

        // 全局顶部拖动区域（覆盖整个窗口上部）
        MouseArea {
            id: globalDragArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: Theme.headerHeight
            z: 1
            onPressed: window.startSystemMove()
            cursorShape: Qt.ArrowCursor
            propagateComposedEvents: true
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0

            // --- 1. Sidebar ---
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.sidebarWidth
                color: Theme.bgWhite
                border.color: Theme.borderLight

                ColumnLayout {
                    anchors.fill: parent
                    anchors.topMargin: Theme.spacingLarge
                    anchors.bottomMargin: Theme.spacingXLarge
                    spacing: Theme.spacingXXLarge

                    // 窗口控制按钮区域
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 30
                        color: "transparent"
                        z: 2
                        
                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 8
                            Rectangle { 
                                width: Theme.iconSizeSmall
                                height: Theme.iconSizeSmall
                                radius: Theme.radiusSmall
                                color: Theme.windowClose
                                scale: closeMouseArea.containsMouse ? 1.1 : 1.0
                                Behavior on scale { NumberAnimation { duration: 100 } }
                                Text {
                                    anchors.centerIn: parent
                                    text: "×"
                                    color: "#5a0000"
                                    font.pixelSize: 10
                                    font.bold: true
                                    visible: closeMouseArea.containsMouse
                                }
                                MouseArea { 
                                    id: closeMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: window.close()
                                    cursorShape: Qt.PointingHandCursor
                                }
                            }
                            Rectangle { 
                                width: Theme.iconSizeSmall
                                height: Theme.iconSizeSmall
                                radius: Theme.radiusSmall
                                color: Theme.windowMinimize
                                scale: minimizeMouseArea.containsMouse ? 1.1 : 1.0
                                Behavior on scale { NumberAnimation { duration: 100 } }
                                Text {
                                    anchors.centerIn: parent
                                    text: "−"
                                    color: "#855a00"
                                    font.pixelSize: 10
                                    font.bold: true
                                    visible: minimizeMouseArea.containsMouse
                                }
                                MouseArea { 
                                    id: minimizeMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: window.showMinimized()
                                    cursorShape: Qt.PointingHandCursor
                                }
                            }
                            Rectangle { 
                                width: Theme.iconSizeSmall
                                height: Theme.iconSizeSmall
                                radius: Theme.radiusSmall
                                color: Theme.windowMaximize
                                scale: maximizeMouseArea.containsMouse ? 1.1 : 1.0
                                Behavior on scale { NumberAnimation { duration: 100 } }
                                Text {
                                    anchors.centerIn: parent
                                    text: "＋"
                                    color: "#006b2e"
                                    font.pixelSize: 10
                                    font.bold: true
                                    visible: maximizeMouseArea.containsMouse
                                }
                                MouseArea { 
                                    id: maximizeMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.topMargin: Theme.spacingMedium
                        Layout.alignment: Qt.AlignHCenter
                        width: Theme.avatarMedium
                        height: Theme.avatarMedium
                        radius: Theme.radiusLarge
                        color: Theme.primary
                        Text { 
                            text: "M"
                            color: Theme.textWhite
                            anchors.centerIn: parent
                            font.bold: true
                            font.pixelSize: Theme.fontSizeLogo
                        }
                    }

                    Repeater {
                        model: [Theme.iconChat, Theme.iconGroup, Theme.iconFolder, Theme.iconSettings]
                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            width: Theme.buttonMedium
                            height: Theme.buttonMedium
                            radius: Theme.radiusLarge
                            color: index === 0 ? Theme.bgHover : (iconMouseArea.containsMouse ? Theme.bgHover : Theme.bgTransparent)
                            scale: iconMouseArea.containsMouse ? 1.05 : 1.0
                            Behavior on color { ColorAnimation { duration: 150 } }
                            Behavior on scale { NumberAnimation { duration: 100 } }
                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.family: fontAwesome.name
                                font.pixelSize: Theme.iconSizeMedium
                                color: index === 0 ? Theme.primary : Theme.textSecondary
                            }
                            MouseArea {
                                id: iconMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                            }
                        }
                    }
                    Item { Layout.fillHeight: true }
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: Theme.avatarMedium
                        height: Theme.avatarMedium
                        radius: Theme.radiusLarge
                        color: Theme.bgAvatar
                        Text { 
                            text: backend.currentUserName.charAt(0)
                            anchors.centerIn: parent
                            font.bold: true
                        }
                    }
                }
            }

            // --- 2. Contact List ---
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.contactListWidth
                color: Theme.sidebarBg
                border.color: Theme.borderLight

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0
                    Label { 
                        text: "Messages"
                        font.pixelSize: Theme.fontSizeTitle
                        font.bold: true
                        padding: Theme.spacingXLarge
                        color: Theme.textPrimary
                    }
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
                            text: "Search..."
                            color: Theme.textPlaceholder
                        }
                    }
                    ListView {
                        id: userListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: backend.onlineUsers
                        clip: true
                        spacing: Theme.spacingSmall
                        delegate: ItemDelegate {
                            width: userListView.width
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
                            onClicked: backend.selectUser(modelData.user_id)
                            contentItem: RowLayout {
                                spacing: 12
                                Rectangle {
                                    width: Theme.avatarLarge
                                    height: Theme.avatarLarge
                                    radius: Theme.radiusLarge
                                    color: Theme.bgAvatar
                                    Text { 
                                        anchors.centerIn: parent
                                        text: modelData.username.charAt(0)
                                        font.bold: true 
                                    }
                                    Rectangle {
                                        width: Theme.iconSizeSmall
                                        height: Theme.iconSizeSmall
                                        radius: Theme.radiusSmall
                                        color: modelData.status === "online" ? Theme.online : Theme.offline
                                        border.color: Theme.textWhite
                                        border.width: Theme.borderWidthMedium
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
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: modelData.status === "online" ? Theme.textPrimary : Theme.textSecondary
                                    }
                                    Label { 
                                        text: modelData.status === "online" ? "Active now" : "Offline"
                                        font.pixelSize: Theme.fontSizeMedium
                                        color: Theme.textSecondary
                                    }
                                }
                                Rectangle {
                                    visible: modelData.unread_count > 0
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

            // --- 3. Chat Main ---
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.bgWhite
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0
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
                            ColumnLayout {
                                spacing: 2
                                Label {
                                    text: {
                                        for (var i = 0; i < backend.onlineUsers.length; i++) 
                                            if (backend.onlineUsers[i].is_current) return backend.onlineUsers[i].username;
                                        return "Select a contact";
                                    }
                                    font.pixelSize: Theme.fontSizeLarge
                                    font.bold: true
                                    color: Theme.textPrimary
                                }
                                RowLayout {
                                    visible: backend.currentChatUserStatus === "online"
                                    Rectangle { 
                                        width: 8
                                        height: 8
                                        radius: 4
                                        color: Theme.online
                                    }
                                    Label { 
                                        text: "Online"
                                        font.pixelSize: Theme.fontSizeMedium
                                        color: Theme.online
                                        font.bold: true
                                    }
                                }
                            }
                            Item { Layout.fillWidth: true }
                            RowLayout {
                                spacing: Theme.spacingXLarge
                                z: 3
                                Text { 
                                    text: Theme.iconPhone
                                    font.family: fontAwesome.name
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
                                Text { 
                                    text: Theme.iconVideo
                                    font.family: fontAwesome.name
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
                                Text { 
                                    text: Theme.iconMore
                                    font.family: fontAwesome.name
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
                    ListView {
                        id: chatList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: backend.messageModel
                        clip: true
                        spacing: Theme.spacingLarge
                        topMargin: Theme.spacingXLarge
                        bottomMargin: Theme.spacingXLarge
                        leftMargin: Theme.spacingXLarge
                        rightMargin: Theme.spacingXLarge
                        
                        // 调试：监听 count 变化
                        onCountChanged: {
                            console.log("[QML ListView] count 变化: ", count)
                        }
                        
                        Component.onCompleted: {
                            console.log("[QML ListView] 初始化完成，model:", model)
                            console.log("[QML ListView] 初始 count:", count)
                        }
                        
                        delegate: ColumnLayout {
                            width: chatList.width - 40
                            spacing: Theme.spacingSmall
                            RowLayout {
                                Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                                layoutDirection: is_mine ? Qt.RightToLeft : Qt.LeftToRight
                                spacing: 10
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
                            Label {
                                Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                                text: Qt.formatDateTime(new Date(timestamp * 1000), "hh:mm")
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                            }
                        }
                    }
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
                                TextField {
                                    id: messageInput
                                    Layout.fillWidth: true
                                    placeholderText: backend.currentChatUserStatus === "online" ? "Write a message..." : "User is offline"
                                    enabled: backend.currentChatUserStatus === "online"
                                    background: Item {}
                                    color: Theme.textPrimary
                                    font.pixelSize: Theme.fontSizeNormal
                                    onAccepted: sendBtn.clicked()
                                }
                                Button {
                                    id: sendBtn
                                    Layout.preferredWidth: Theme.buttonSmall
                                    Layout.preferredHeight: Theme.buttonSmall
                                    enabled: backend.currentChatUserStatus === "online" && messageInput.text.trim().length > 0
                                    scale: hovered ? 1.05 : 1.0
                                    hoverEnabled: true
                                    Behavior on scale { NumberAnimation { duration: 100 } }
                                    contentItem: Text { 
                                        text: Theme.iconSend
                                        color: Theme.textWhite
                                        font.family: fontAwesome.name
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
    }
    onClosing: backend.stop()
}
