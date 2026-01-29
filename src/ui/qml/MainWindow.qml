import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtGraphicalEffects 1.15

// 主窗口组件：程序的根容器，实现无边框、自定义拖拽和三栏布局
ApplicationWindow {
    id: window
    visible: true
    width: Theme.windowWidth
    height: Theme.windowHeight
    minimumWidth: 800            // 限制最小宽度，防止布局乱掉
    minimumHeight: 600           // 限制最小高度
    // flags: 设置为无边框窗口，同时保留原生窗口特性
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"         // 设置背景透明，以便实现圆角效果

    // 窗口背景矩形
    background: Rectangle {
        color: "transparent"
        radius: Theme.radiusWindow // 窗口圆角
    }

    // 动态加载 FontAwesome 字体，用于显示矢量图标
    FontLoader {
        id: fontAwesome
        source: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf"
    }

    // 与 Python 后端 (backend) 的信号连接
    Connections {
        target: backend
        // 当收到或发送新消息时，调用聊天区域的滚动方法
        function onNewMessageReceived(msg) {
            chatArea.scrollToBottom()
        }
        function onNewMessageSent(msg) {
            chatArea.scrollToBottom()
        }
        function onGroupMessageReceived(msg) {
            chatArea.scrollToBottom()
        }
    }

    // 主内容容器：包裹整个 UI 的矩形，应用圆角和阴影
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        anchors.margins: 0
        radius: Theme.radiusWindow
        color: Theme.bgWhite
        clip: true               // 裁剪超出圆角的子元素
        antialiasing: true       // 开启抗锯齿
        smooth: true

        // 使用 OpacityMask 确保内容区域严格遵循容器的圆角边界
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

        // 窗口顶部拖拽区域：由于设置了 FramelessWindowHint，需要手动实现拖拽移动窗口
        MouseArea {
            id: globalDragArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: Theme.headerHeight // 拖拽区域通常与头部高度一致
            z: 1                       // 位于内容层之上
            // 调用系统底层方法开始移动窗口
            onPressed: window.startSystemMove()
            cursorShape: Qt.ArrowCursor
            propagateComposedEvents: true // 允许事件向下传递（如按钮点击）
        }

        // 右下角调整窗口大小的敏感区域
        MouseArea {
            id: resizeArea
            width: 20
            height: 20
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            z: 10
            cursorShape: Qt.SizeFDiagCursor // 鼠标变更为对角线调整样式
            hoverEnabled: true
            
            property point clickPos: Qt.point(0, 0)
            
            onPressed: {
                clickPos = Qt.point(mouse.x, mouse.y)
            }
            
            // 手动计算并设置窗口大小
            onPositionChanged: {
                if (pressed) {
                    var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
                    var newWidth = window.width + delta.x
                    var newHeight = window.height + delta.y
                    
                    // 检查是否达到最小尺寸限制
                    if (newWidth >= window.minimumWidth) {
                        window.width = newWidth
                    }
                    if (newHeight >= window.minimumHeight) {
                        window.height = newHeight
                    }
                }
            }
        }

        // 主布局：水平排列三个核心模块
        RowLayout {
            anchors.fill: parent
            spacing: 0

            // 1. 左侧窄边栏：功能导航和个人头像
            Sidebar {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.sidebarWidth
                currentUserName: backend.currentUserName
                fontAwesomeFamily: fontAwesome.name
            }

            // 2. 中间联系人列表：私聊和群组的混合列表
            ContactList {
                Layout.fillHeight: true
                Layout.preferredWidth: Theme.contactListWidth
                Layout.maximumWidth: Theme.contactListWidth
                onlineUsers: backend.onlineUsers
                groupList: backend.groupList
                // 选中联系人时的逻辑
                onUserSelected: function(userId) {
                    backend.selectUser(userId)
                    updateChatAreaForUser() // 更新聊天区状态
                }
                // 选中群组时的逻辑
                onGroupSelected: function(groupId) {
                    backend.selectGroup(groupId)
                    updateChatAreaForGroup(groupId) // 更新聊天区状态
                }
                // 点击创建群组按钮
                onCreateGroup: function() {
                    createGroupDialog.open()
                }
            }

            // 3. 右侧主聊天区域：显示对话详情和输入框
            ChatArea {
                id: chatArea
                Layout.fillWidth: true    // 自动占据所有剩余空间
                Layout.fillHeight: true
                messageModel: backend.messageModel
                onlineUsers: backend.onlineUsers
                currentChatUserStatus: backend.currentChatUserStatus
                fontAwesomeFamily: fontAwesome.name
                // 发送消息的回调
                onSendMessage: function(text) {
                    backend.sendMessage(text)
                }
            }
        }
    }

    // 模态对话框：创建群组
    CreateGroupDialog {
        id: createGroupDialog
        onlineUsers: backend.onlineUsers
        onCreateGroup: function(groupName, memberIds) {
            backend.createGroup(groupName, memberIds)
        }
    }

    // 辅助函数：切换到私聊模式，重置群组相关属性
    function updateChatAreaForUser() {
        chatArea.isGroupChat = false
        chatArea.groupName = ""
        chatArea.groupMemberCount = 0
    }

    // 辅助函数：切换到群聊模式，设置群组名称和成员数
    function updateChatAreaForGroup(groupId) {
        chatArea.isGroupChat = true
        var groups = backend.groupList
        for (var i = 0; i < groups.length; i++) {
            if (groups[i].group_id === groupId) {
                chatArea.groupName = groups[i].group_name
                chatArea.groupMemberCount = groups[i].member_count
                break
            }
        }
    }

    // 当窗口关闭时，通知后端执行清理工作（如销毁临时数据库）
    onClosing: backend.stop()
}
