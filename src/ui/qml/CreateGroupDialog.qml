import QtQuick 2.15              // 基础组件
import QtQuick.Controls 2.15     // 对话框、按钮等
import QtQuick.Layouts 1.15      // 布局管理器
import QtGraphicalEffects 1.15   // 模糊、阴影等特效

// 创建群组对话框：提供一个全屏模态窗口来配置新群组
Dialog {
    id: dialog
    modal: true                  // 模态对话框，阻断下层交互
    width: 760                   // 宽度
    height: 620                  // 高度
    x: (parent.width - width) / 2  // 居中定位
    y: (parent.height - height) / 2
    padding: 0                   // 移除内边距，方便自定义布局
    closePolicy: Popup.CloseOnEscape // 按下 Esc 键关闭

    property var onlineUsers: []  // 待选用户列表（从后端传入）
    property var onCreateGroup: function(groupName, memberIds) {} // 创建按钮点击回调
    property string searchText: "" // 搜索框文本
    property int selectedUserCount: 0 // 已选中的用户计数，用于实时刷新 UI

    // 模态背景：在对话框弹出时，将底层界面变白并模糊处理
    Overlay.modal: Rectangle {
        color: "#66ffffff"       // 半透明白底
        
        layer.enabled: true
        layer.effect: FastBlur { // 快速模糊特效
            radius: 16
        }
    }

    // 对话框主体背景
    background: Rectangle {
        color: Theme.bgWhite
        radius: 40               // 大圆角设计，符合现代审美
        border.color: Theme.bgWhite
        border.width: 1
        
        // 外部大阴影效果
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 40
            radius: 60
            samples: 121
            color: "#20000000"   // 柔和的深色阴影
            spread: 0
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 顶部控制区域：放置关闭按钮
        Rectangle {
            width: parent.width
            height: 0            // 高度为0，按钮通过绝对坐标定位
            z: 100               // 确保按钮在最上层

            // macOS 风格的红色关闭按钮
            Button {
                x: 24
                y: 24
                width: 12
                height: 12
                hoverEnabled: true

                contentItem: Text {
                    text: "✕"        // 关闭图标
                    font.pixelSize: 12
                    color: Theme.textBlack
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    opacity: parent.hovered ? 1.0 : 0.0 // 仅在悬停时显示 "X"
                    Behavior on opacity { NumberAnimation { duration: 200 } }
                }

                background: Rectangle {
                    radius: parent.hovered ? 10 : 6    // 悬停时稍微变大
                    color: "#ff5f57"                   // 经典的 macOS 关闭按钮红
                    Behavior on radius { NumberAnimation { duration: 200 } }
                }

                // 按钮大小变化的动画
                Behavior on width { NumberAnimation { duration: 200 } }
                Behavior on height { NumberAnimation { duration: 200 } }

                onHoveredChanged: {
                    if (hovered) {
                        width = 14
                        height = 14
                    } else {
                        width = 12
                        height = 12
                    }
                }

                onClicked: dialog.reject() // 点击关闭（拒绝操作）
            }
        }

        // 顶部信息输入区：头像 + 群名
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            color: "transparent"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 56
                anchors.bottomMargin: 32
                spacing: 32

                // 模拟头像上传区域
                Rectangle {
                    Layout.preferredWidth: 80
                    Layout.preferredHeight: 80
                    radius: 40
                    color: Theme.bgInputArea
                    border.width: 2
                    border.color: Theme.borderGray

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 2

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "📷"
                            font.pixelSize: 24
                        }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: "AVATAR"
                            font.pixelSize: 9
                            font.bold: true
                            color: Theme.textSecondary
                            font.letterSpacing: 2
                        }
                    }

                    // 右下角的蓝色 "+" 角标
                    Rectangle {
                        width: 28
                        height: 28
                        radius: 14
                        color: Theme.primary
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.rightMargin: -2
                        anchors.bottomMargin: -2
                        border.width: 2
                        border.color: Theme.bgWhite

                        Text {
                            anchors.centerIn: parent
                            text: "+"
                            color: Theme.textWhite
                            font.pixelSize: 16
                            font.bold: true
                        }

                        layer.enabled: true
                        layer.effect: DropShadow {
                            horizontalOffset: 0
                            verticalOffset: 2
                            radius: 4
                            samples: 9
                            color: "#40000000"
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onEntered: parent.border.color = Theme.primary
                        onExited: parent.border.color = Theme.borderGray
                    }
                }

                // 群组名称输入区域
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    Label {
                        text: "NEW GROUP CONVERSATION"
                        font.pixelSize: 10
                        font.bold: true
                        color: Theme.textSecondary
                        font.letterSpacing: 2
                    }

                    TextField {
                        id: groupNameInput
                        Layout.fillWidth: true
                        placeholderText: "Enter group name..."
                        font.pixelSize: 30                  // 特大号字体
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary

                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }
            }
        }

        // 搜索框区域
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 88
            color: "transparent"

            Rectangle {
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 16
                anchors.bottomMargin: 32
                radius: 24
                color: "#f0f0f0"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 12

                    Text {
                        text: "🔍"
                        font.pixelSize: 20
                        color: searchInput.activeFocus ? Theme.primary : Theme.textSecondary
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }

                    TextField {
                        id: searchInput
                        Layout.fillWidth: true
                        placeholderText: "Search contacts by name, role or department..."
                        font.pixelSize: 14
                        color: Theme.textPrimary
                        onTextChanged: searchText = text

                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }
            }
        }

        // 成员选择区域：网格布局展示所有在线用户
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.bgWhite

            ScrollView {
                id: scrollView
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 0
                anchors.bottomMargin: 40
                clip: true
                contentWidth: availableWidth

                // Flow 布局：根据窗口宽度自动流式排布子组件
                Flow {
                    width: scrollView.availableWidth
                    spacing: 20

                    Repeater {
                        model: onlineUsers // 遍历在线用户
                        Rectangle {
                            id: card
                            // 每一个卡片项的逻辑
                            property bool isSelected: !!modelData.selected

                            width: (scrollView.availableWidth - 80) / 5 // 一行显示 5 个
                            height: 140
                            radius: 24
                            color: Theme.bgWhite
                            // 选中时边框加粗并变色
                            border.width: isSelected ? 2 : 1
                            border.color: isSelected ? "#64748b" : "#e5e7eb"

                            // 卡片悬浮阴影效果
                            layer.enabled: true
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: isSelected ? 6 : 1
                                radius: isSelected ? 12 : 6
                                samples: isSelected ? 25 : 13
                                color: isSelected ? "#12000000" : "#06000000"
                                spread: 0
                            }

                            Behavior on color { ColorAnimation { duration: 200 } }
                            Behavior on border.color { ColorAnimation { duration: 200 } }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 0

                                // 右上角的小圆点选中状态指示器
                                Rectangle {
                                    Layout.alignment: Qt.AlignRight
                                    Layout.topMargin: 0
                                    width: 18
                                    height: 18
                                    radius: 9
                                    color: isSelected ? Theme.primary : "transparent"
                                    border.width: 2
                                    border.color: isSelected ? Theme.primary : "#e5e7eb"

                                    Text {
                                        visible: isSelected
                                        anchors.centerIn: parent
                                        text: "✓"
                                        color: Theme.textWhite
                                        font.pixelSize: 10
                                        font.bold: true
                                    }

                                    Behavior on color { ColorAnimation { duration: 200 } }
                                    Behavior on border.color { ColorAnimation { duration: 200 } }
                                }

                                Item { Layout.fillHeight: true; Layout.minimumHeight: 4 }

                                // 成员头像
                                Rectangle {
                                    Layout.alignment: Qt.AlignHCenter
                                    width: 52
                                    height: 52
                                    radius: 16
                                    color: Theme.bgAvatar

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.username.charAt(0).toUpperCase()
                                        font.pixelSize: 22
                                        font.bold: true
                                        color: Theme.textPrimary
                                    }

                                    layer.enabled: true
                                    layer.effect: DropShadow {
                                        horizontalOffset: 0
                                        verticalOffset: 1
                                        radius: 3
                                        samples: 7
                                        color: "#12000000"
                                    }
                                }

                                Item { Layout.preferredHeight: 10 }

                                // 成员名称和状态文字
                                ColumnLayout {
                                    Layout.alignment: Qt.AlignHCenter
                                    spacing: 2

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.username
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: Theme.textPrimary
                                        elide: Text.ElideRight
                                        maximumLineCount: 1
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.status === "online" ? "Online" : "Offline"
                                        font.pixelSize: 9
                                        font.weight: Font.Medium
                                        color: {
                                            if (isSelected) {
                                                return Theme.primary
                                            }
                                            return modelData.status === "online" ? "#10b981" : "#94a3b8"
                                        }
                                    }
                                }

                                Item { Layout.fillHeight: true; Layout.minimumHeight: 4 }
                            }

                            property real scale: 1.0 // 控制缩放的内部属性

                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                z: 10               // 确保点击层在最上
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true

                                onEntered: {
                                    parent.scale = 1.05 // 鼠标悬停时放大
                                    if (!isSelected) {
                                        parent.border.color = "#cbd5e1"
                                    }
                                }
                                onExited: {
                                    parent.scale = 1.0 // 鼠标离开时恢复
                                    if (!isSelected) {
                                        parent.border.color = "#e5e7eb"
                                    }
                                }

                                onClicked: {
                                    // 核心逻辑：切换选中状态并更新计数
                                    card.isSelected = !card.isSelected
                                    modelData.selected = card.isSelected
                                    selectedUserCount = selectedCount() // 刷新底部统计
                                    console.log("Card toggled for: " + modelData.username + ", now: " + card.isSelected)
                                }
                            }

                            // 变换效果：模拟点击时的微弱“下沉”深度感
                            transform: Translate {
                                y: mouseArea.pressed ? 2 : 0
                                Behavior on y { NumberAnimation { duration: 50 } }
                            }

                            // 缩放平滑过渡
                            Behavior on scale {
                                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                            }
                        }
                    }
                }
            }
        }
        // 底部操作栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: "#fafafa"
            border.width: 1
            border.color: Theme.borderLight

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                spacing: 20

                // 已选成员的小头像堆叠显示
                RowLayout {
                    spacing: 0

                    Repeater {
                        model: Math.min(selectedUserCount, 2) // 最多并列显示两个头像

                        Rectangle {
                            width: 44
                            height: 44
                            radius: 22
                            color: Theme.bgAvatar
                            border.width: 4
                            border.color: "#fafafa"
                            z: 10 - index                    // 堆叠层级：第一个在最上面

                            Text {
                                anchors.centerIn: parent
                                text: getSelectedUsers()[index].username.charAt(0)
                                font.pixelSize: 16
                                font.bold: true
                                color: Theme.textPrimary
                            }

                            layer.enabled: true
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: 2
                                radius: 4
                                samples: 9
                                color: "#20000000"
                            }
                        }
                    }

                    // 如果选了超过两个，显示 +N 的圆形指示
                    Rectangle {
                        visible: selectedUserCount > 2
                        width: 44
                        height: 44
                        radius: 22
                        color: Theme.bgInputArea
                        border.width: 4
                        border.color: "#fafafa"
                        z: 8

                        Label {
                            anchors.centerIn: parent
                            text: "+" + (selectedUserCount - 2)
                            font.pixelSize: 11
                            font.bold: true
                            color: Theme.textSecondary
                        }

                        layer.enabled: true
                        layer.effect: DropShadow {
                            horizontalOffset: 0
                            verticalOffset: 2
                            radius: 4
                            samples: 9
                            color: "#20000000"
                        }
                    }
                }

                // 底部文字提示：显示当前选中的成员数
                ColumnLayout {
                    spacing: 2

                    Label {
                        text: selectedUserCount + " Members Selected"
                        font.pixelSize: 14
                        font.bold: true
                        color: Theme.textPrimary
                    }

                    Label {
                        text: "READY TO START CONVERSATION"
                        font.pixelSize: 11
                        font.weight: Font.Medium
                        color: Theme.textSecondary
                        font.letterSpacing: 1.5
                    }
                }

                Item { Layout.fillWidth: true } // 弹簧：推开按钮

                // 底部按钮组：取消与创建
                RowLayout {
                    spacing: 16

                    // 取消按钮
                    Button {
                        Layout.preferredWidth: 100
                        Layout.preferredHeight: 48
                        hoverEnabled: true

                        contentItem: Text {
                            text: "Cancel"
                            font.pixelSize: 14
                            font.bold: true
                            color: parent.hovered ? Theme.textPrimary : Theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        background: Rectangle {
                            radius: 16
                            color: parent.hovered ? Theme.bgInputArea : "transparent"
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }

                        onClicked: dialog.reject()
                    }

                    // 创建按钮：仅在群名非空且选了成员时启用
                    Button {
                        id: createBtn
                        Layout.preferredWidth: 140
                        Layout.preferredHeight: 48
                        enabled: groupNameInput.text.trim().length > 0 && selectedUserCount > 0
                        hoverEnabled: true

                        contentItem: Text {
                            text: "Create Space"
                            font.pixelSize: 14
                            font.bold: true
                            color: Theme.textWhite
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: 16
                            color: parent.enabled ? (parent.hovered ? "#2563eb" : Theme.primary) : Theme.offline

                            Behavior on color { ColorAnimation { duration: 150 } }

                            // 按钮发光阴影特效
                            layer.enabled: parent.enabled
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: parent.hovered ? 18 : 12
                                radius: parent.hovered ? 28 : 20
                                samples: parent.hovered ? 57 : 41
                                color: "#353b82f6"
                                spread: 0
                                Behavior on verticalOffset { NumberAnimation { duration: 150 } }
                                Behavior on radius { NumberAnimation { duration: 150 } }
                            }

                            // 悬停时按钮微弱上升
                            transform: Translate {
                                y: parent.hovered && parent.enabled ? -2 : 0
                                Behavior on y { NumberAnimation { duration: 150 } }
                            }
                        }

                        onClicked: {
                            var selectedUserIds = []
                            for (var i = 0; i < onlineUsers.length; i++) {
                                if (onlineUsers[i].selected) {
                                    selectedUserIds.push(onlineUsers[i].user_id)
                                }
                            }
                            
                            if (groupNameInput.text.trim().length > 0 && selectedUserIds.length > 0) {
                                onCreateGroup(groupNameInput.text.trim(), selectedUserIds)
                                dialog.accept()
                                reset() // 提交后重置数据
                            }
                        }
                    }
                }
            }
        }
    }

    // 内部 JS 逻辑：辅助函数用于计算状态
    function selectedCount() {
        var count = 0
        for (var i = 0; i < onlineUsers.length; i++) {
            if (onlineUsers[i].selected) {
                count++
            }
        }
        return count
    }

    function getSelectedUsers() {
        var selected = []
        for (var i = 0; i < onlineUsers.length; i++) {
            if (onlineUsers[i].selected) {
                selected.push(onlineUsers[i])
            }
        }
        return selected
    }

    // 重置对话框状态，清空输入和选中项
    function reset() {
        groupNameInput.clear()
        searchInput.clear()
        for (var i = 0; i < onlineUsers.length; i++) {
            onlineUsers[i].selected = false
        }
        selectedUserCount = 0
    }

    onRejected: {
        reset()
    }
}
