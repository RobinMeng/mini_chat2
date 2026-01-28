import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtGraphicalEffects 1.15

ApplicationWindow {
    id: window
    visible: true
    width: Theme.windowWidth
    height: Theme.windowHeight
    minimumWidth: 800
    minimumHeight: 600
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
            // 通过组件 ID 引用聊天区域
            chatArea.scrollToBottom()
        }
        function onNewMessageSent(msg) {
            // 通过组件 ID 引用聊天区域
            chatArea.scrollToBottom()
        }
        function onGroupMessageReceived(msg) {
            // 群组消息接收
            chatArea.scrollToBottom()
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

        // 右下角调整窗口大小区域
        MouseArea {
            id: resizeArea
            width: 20
            height: 20
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            z: 10
            cursorShape: Qt.SizeFDiagCursor
            hoverEnabled: true
            
            property point clickPos: Qt.point(0, 0)
            
            onPressed: {
                clickPos = Qt.point(mouse.x, mouse.y)
            }
            
            onPositionChanged: {
                if (pressed) {
                    var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
                    var newWidth = window.width + delta.x
                    var newHeight = window.height + delta.y
                    
                    // 限制最小尺寸
                    if (newWidth >= window.minimumWidth) {
                        window.width = newWidth
                    }
                    if (newHeight >= window.minimumHeight) {
                        window.height = newHeight
                    }
                }
            }
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0

            // 左侧边栏
            Sidebar {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.sidebarWidth
                currentUserName: backend.currentUserName
                fontAwesomeFamily: fontAwesome.name
            }

            // 中间聊天列表（群组 + 私聊）
            ContactList {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.contactListWidth
                Layout.maximumWidth: Theme.contactListWidth
                onlineUsers: backend.onlineUsers
                groupList: backend.groupList
                onUserSelected: function(userId) {
                    backend.selectUser(userId)
                    updateChatAreaForUser()
                }
                onGroupSelected: function(groupId) {
                    backend.selectGroup(groupId)
                    updateChatAreaForGroup(groupId)
                }
                onCreateGroup: function() {
                    createGroupDialog.open()
                }
            }

            // 右侧聊天区域
            ChatArea {
                id: chatArea
                Layout.fillWidth: true
                Layout.fillHeight: true
                messageModel: backend.messageModel
                onlineUsers: backend.onlineUsers
                currentChatUserStatus: backend.currentChatUserStatus
                fontAwesomeFamily: fontAwesome.name
                onSendMessage: function(text) {
                    backend.sendMessage(text)
                }
            }
        }
    }

    // 创建群组对话框
    CreateGroupDialog {
        id: createGroupDialog
        onlineUsers: backend.onlineUsers
        onCreateGroup: function(groupName, memberIds) {
            backend.createGroup(groupName, memberIds)
        }
    }

    // 辅助函数：更新聊天区域（私聊）
    function updateChatAreaForUser() {
        chatArea.isGroupChat = false
        chatArea.groupName = ""
        chatArea.groupMemberCount = 0
    }

    // 辅助函数：更新聊天区域（群聊）
    function updateChatAreaForGroup(groupId) {
        chatArea.isGroupChat = true
        // 从 groupList 中找到对应的群组
        var groups = backend.groupList
        for (var i = 0; i < groups.length; i++) {
            if (groups[i].group_id === groupId) {
                chatArea.groupName = groups[i].group_name
                chatArea.groupMemberCount = groups[i].member_count
                break
            }
        }
    }

    onClosing: backend.stop()
}
