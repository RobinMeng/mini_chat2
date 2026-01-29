import QtQuick 2.15              // 导入 QtQuick 基础库，提供 Rectangle, Text 等核心组件
import QtQuick.Controls 2.15     // 导入 QtQuick 控件库，提供 Button, TextField, Label 等标准控件
import QtQuick.Layouts 1.15      // 导入布局库，提供 ColumnLayout, RowLayout, GridLayout 等自动布局工具

// 聊天区域组件：负责显示对话详情，包含顶部的用户信息头部、中间的消息列表和底部的输入框
Rectangle {
    color: Theme.bgWhite         // 设置背景颜色为主题定义的白色

    // 定义属性供外部绑定和交互
    property var messageModel    // 消息列表的数据模型（通常来自 Python 后端）
    property var onlineUsers: [] // 在线用户列表数组
    property string currentChatUserStatus: "offline" // 当前聊天对象的在线状态
    property var fontAwesomeFamily: "" // 图标字体的名称
    property var onSendMessage: function(text) {} // 发送消息的回调函数
    property bool isGroupChat: false  // 标识当前是否为群聊模式
    property string groupName: ""      // 当前聊天群组的名称
    property int groupMemberCount: 0  // 当前群组的成员总数

    // scrollToBottom 函数：提供给外部调用，用于将消息列表滚动到最底部
    function scrollToBottom() {
        // 使用 Qt.callLater 确保在界面刷新后的下一帧执行滚动，避免布局未计算完成导致的滚动不到位
        Qt.callLater(function() {
            chatList.forceLayout()      // 强制 ListView 重新计算布局
            chatList.positionViewAtEnd() // 将视图滚动到最末尾
        })
    }

    // 主列布局：将头部、列表、输入区垂直排列
    ColumnLayout {
        anchors.fill: parent           // 填充父容器（即外部的 Rectangle）
        spacing: 0                     // 组件之间不留间距，边界靠 border 区分

        // 聊天头部：显示当前聊天对象信息和功能按钮
        Rectangle {
            Layout.fillWidth: true     // 自动填满宽度
            height: Theme.headerHeight // 使用主题定义的统一高度
            color: Theme.bgWhite       // 背景白色
            border.color: Theme.borderLight // 底部边框线颜色

            // 水平布局：左右排列用户信息和操作按钮
            RowLayout {
                anchors.fill: parent   // 填充头部矩形
                anchors.leftMargin: Theme.spacingXXLarge  // 左边距
                anchors.rightMargin: Theme.spacingXXLarge // 右边距
                z: 2                   // 确保层级在上方

                // 嵌套列布局：上下排列用户昵称和在线状态/成员数
                ColumnLayout {
                    spacing: 2         // 内部元素垂直间距
                    Label {
                        // 动态显示名称：群聊显示群名，私聊显示对方用户名
                        text: {
                            if (isGroupChat) {
                                return groupName || "Group Chat"
                            }
                            // 查找当前正在聊天的用户
                            for (var i = 0; i < onlineUsers.length; i++)
                                if (onlineUsers[i].is_current) return onlineUsers[i].username;
                            return "Select a contact";
                        }
                        font.pixelSize: Theme.fontSizeLarge // 使用大号字体
                        font.bold: true                     // 加粗
                        color: Theme.textPrimary            // 主文字颜色
                    }

                    // 状态行：显示绿色小圆点和状态文字
                    RowLayout {
                        // 仅在群聊或私聊对象在线时显示
                        visible: isGroupChat || currentChatUserStatus === "online"
                        
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4                       // 圆角为宽度一半，即正圆
                            color: isGroupChat ? "#10b981" : Theme.online // 群聊用特定绿，私聊用主题在线绿
                        }

                        Label {
                            // 群聊显示成员数，私聊显示 Online
                            text: isGroupChat ? (groupMemberCount + " members") : "Online"
                            font.pixelSize: Theme.fontSizeMedium
                            color: isGroupChat ? "#10b981" : Theme.online
                            font.bold: true
                        }
                    }
                }

                // 弹簧组件：将右侧的按钮推向最右边
                Item { Layout.fillWidth: true }

                // 右侧功能按钮组
                RowLayout {
                    spacing: Theme.spacingXLarge
                    z: 3

                    // 电话按钮：使用 Text 配合 FontAwesome 字体实现图标
                    Text {
                        text: Theme.iconPhone
                        font.family: fontAwesomeFamily
                        font.pixelSize: Theme.iconSizeMedium
                        // 根据鼠标悬停状态切换颜色
                        color: phoneMouseArea.containsMouse ? Theme.primary : Theme.textSecondary
                        // 根据鼠标悬停状态缩放
                        scale: phoneMouseArea.containsMouse ? 1.1 : 1.0
                        // 颜色和缩放的平滑动画过渡
                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        MouseArea {
                            id: phoneMouseArea
                            anchors.fill: parent
                            hoverEnabled: true               // 开启悬停检测
                            cursorShape: Qt.PointingHandCursor // 鼠标移入变手型
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

                    // 更多功能按钮
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

        // 核心组件：消息列表（使用 ListView 实现高效滚动和复用）
        ListView {
            id: chatList
            Layout.fillWidth: true     // 占据剩余所有宽度
            Layout.fillHeight: true    // 占据中间所有剩余高度
            model: messageModel        // 绑定消息模型
            clip: true                 // 裁剪超出范围的内容
            spacing: Theme.spacingLarge // 消息项之间的垂直间距
            topMargin: Theme.spacingXLarge    // 列表顶部留白
            bottomMargin: Theme.spacingXLarge // 列表底部留白
            leftMargin: Theme.spacingXLarge   // 列表左边距
            rightMargin: Theme.spacingXLarge  // 列表右边距

            // 当消息数量改变（发送或接收新消息）时，自动滚动到最下方
            onCountChanged: {
                Qt.callLater(function() {
                    chatList.forceLayout()
                    chatList.positionViewAtEnd()
                })
            }

            // delegate 渲染每一条消息的样式
            delegate: ColumnLayout {
                width: chatList.width - 40 // 宽度减去边距
                spacing: Theme.spacingSmall

                // 消息行：包含头像和气泡
                RowLayout {
                    // 如果是“我的消息”，右对齐；否则左对齐
                    Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                    // 如果是“我的消息”，排列方向从右向左
                    layoutDirection: is_mine ? Qt.RightToLeft : Qt.LeftToRight
                    spacing: 10

                    // 头像显示：仅在对方发送的消息中显示
                    Rectangle {
                        visible: !is_mine
                        width: Theme.avatarSmall
                        height: Theme.avatarSmall
                        radius: Theme.radiusMedium
                        color: Theme.bgAvatar

                        Text {
                            anchors.centerIn: parent
                            text: from_username.charAt(0) // 取用户名的第一个字
                            font.pixelSize: 12
                        }
                    }

                    // 消息气泡矩形
                    Rectangle {
                        Layout.maximumWidth: chatList.width * 0.6 // 最大宽度占屏幕 60%
                        // 根据文字大小自动计算宽高，加上内边距
                        width: msgText.implicitWidth + 30
                        height: msgText.implicitHeight + 24
                        radius: Theme.radiusBubble
                        // 我发的用主色，对方发的用浅灰色
                        color: is_mine ? Theme.primary : Theme.receivedBubble
                        border.color: is_mine ? Theme.primary : Theme.borderLight

                        Text {
                            id: msgText
                            text: content            // 显示消息内容
                            anchors.centerIn: parent // 文字在气泡中居中
                            color: is_mine ? Theme.textWhite : Theme.textPrimary
                            font.pixelSize: Theme.fontSizeNormal
                            wrapMode: Text.Wrap      // 文字过长自动换行
                            width: parent.width - 30 // 文字实际可用宽度
                        }
                    }
                }

                // 时间戳标签：显示在气泡下方
                Label {
                    Layout.alignment: is_mine ? Qt.AlignRight : Qt.AlignLeft
                    text: Qt.formatDateTime(new Date(timestamp * 1000), "hh:mm")
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                }
            }
        }

        // 输入区域容器
        Rectangle {
            Layout.fillWidth: true
            height: Theme.inputAreaHeight // 固定高度
            color: Theme.bgWhite

            // 圆角输入框背景
            Rectangle {
                anchors.fill: parent
                anchors.margins: Theme.spacingLarge
                radius: Theme.radiusXLarge
                color: Theme.bgInputArea    // 浅灰色输入背景
                border.color: Theme.bgAvatar

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingLarge
                    anchors.rightMargin: 8

                    // 文本输入框组件
                    TextField {
                        id: messageInput
                        Layout.fillWidth: true
                        placeholderText: {
                            if (isGroupChat) {
                                return "Write a message to group..."
                            }
                            return currentChatUserStatus === "online" ? "Write a message..." : "User is offline"
                        }
                        // 对方离线且非群聊时，禁用输入
                        enabled: isGroupChat || currentChatUserStatus === "online"
                        background: Item {}  // 隐藏原生的边框背景，使用外层的 Rectangle
                        color: Theme.textPrimary
                        font.pixelSize: Theme.fontSizeNormal
                        // 按回车键时触发发送按钮的点击事件
                        onAccepted: sendBtn.clicked()
                    }

                    // 发送按钮：带图标的圆形/圆角矩形
                    Button {
                        id: sendBtn
                        Layout.preferredWidth: Theme.buttonSmall
                        Layout.preferredHeight: Theme.buttonSmall
                        // 仅在有内容输入且对方在线（或群聊）时可用
                        enabled: (isGroupChat || currentChatUserStatus === "online") && messageInput.text.trim().length > 0
                        scale: hovered ? 1.05 : 1.0
                        hoverEnabled: true
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        // 按钮内的图标
                        contentItem: Text {
                            text: Theme.iconSend
                            color: Theme.textWhite
                            font.family: fontAwesomeFamily
                            font.pixelSize: Theme.iconSizeMedium
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        // 按钮背景样式
                        background: Rectangle {
                            radius: Theme.radiusMedium
                            // 根据启用状态和悬停状态切换颜色
                            color: parent.enabled ? (parent.hovered ? "#2563eb" : Theme.primary) : Theme.offline
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        // 点击事件处理
                        onClicked: {
                            onSendMessage(messageInput.text) // 调用发送回调
                            messageInput.clear()              // 清空输入框
                        }
                    }
                }
            }
        }
    }
}
