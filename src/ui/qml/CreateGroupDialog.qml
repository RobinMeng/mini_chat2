import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

// 创建群组对话框
Dialog {
    id: dialog
    modal: true
    width: 760
    height: 620
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    padding: 0
    closePolicy: Popup.CloseOnEscape

    property var onlineUsers: []
    property var onCreateGroup: function(groupName, memberIds) {}
    property string searchText: ""
    property int selectedUserCount: 0  // 添加选中计数器

    // 背景模糊遮罩
    Overlay.modal: Rectangle {
        color: "#66ffffff"  // 半透明白色
        
        layer.enabled: true
        layer.effect: FastBlur {
            radius: 16
        }
    }

    background: Rectangle {
        color: Theme.bgWhite
        radius: 40
        border.color: Theme.bgWhite
        border.width: 1
        
        // 阴影效果
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 40
            radius: 60
            samples: 121
            color: "#20000000"
            spread: 0
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 关闭按钮（左上角红点）
        Rectangle {
            width: parent.width
            height: 0
            z: 100

            Button {
                x: 24
                y: 24
                width: 12
                height: 12
                hoverEnabled: true

                contentItem: Text {
                    text: "✕"
                    font.pixelSize: 12
                    color: Theme.textBlack
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    opacity: parent.hovered ? 1.0 : 0.0
                    Behavior on opacity { NumberAnimation { duration: 200 } }
                }

                background: Rectangle {
                    radius: parent.hovered ? 10 : 6
                    color: "#ff5f57"
                    Behavior on radius { NumberAnimation { duration: 200 } }
                }

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

                onClicked: dialog.reject()
            }
        }

        // 顶部区域：头像 + 群组名
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 140  // 增加高度
            color: "transparent"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 56  // 增加顶部边距，为关闭按钮留空间
                anchors.bottomMargin: 32
                spacing: 32

                // 群组头像上传
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
                            text: "📷"  // Camera emoji
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

                    // 添加按钮
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

                // 群组名输入
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
                        font.pixelSize: 30
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
            Layout.preferredHeight: 88  // 增加高度以增加上下间距
            color: "transparent"

            Rectangle {
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 16
                anchors.bottomMargin: 32  // 增加底部间距
                radius: 24
                color: "#f0f0f0"  // 淡灰色背景

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 12

                    Text {
                        text: "🔍"  // Search emoji
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

        // 成员网格区域
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.bgWhite

            ScrollView {
                id: scrollView
                anchors.fill: parent
                anchors.leftMargin: 40
                anchors.rightMargin: 40
                anchors.topMargin: 0  // 移除顶部边距，间距由搜索框的 bottomMargin 控制
                anchors.bottomMargin: 40
                clip: true
                contentWidth: availableWidth  // 明确设置内容宽度

                // 使用 Flow 布局替代 GridLayout
                Flow {
                    width: scrollView.availableWidth  // 使用 ScrollView 的可用宽度
                    spacing: 20

                    Repeater {
                        model: onlineUsers
                        Rectangle {
                            id: card
                            // ✅ 使用 !! 确保初始化为布尔值，避免 undefined 错误
                            property bool isSelected: !!modelData.selected

                            width: (scrollView.availableWidth - 80) / 5
                            height: 140
                            radius: 24
                            color: Theme.bgWhite  // ✅ 选中时不再变化颜色，始终保持白色
                            border.width: isSelected ? 2 : 1
                            border.color: isSelected ? "#64748b" : "#e5e7eb"

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

                                // 选中指示器（小圆点）
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

                                // 用户头像
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

                                // 用户信息
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

                            property real scale: 1.0

                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                z: 10  // ✅ 提升层级，确保在布局元素之上
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true

                                onEntered: {
                                    parent.scale = 1.05
                                    if (!isSelected) {
                                        parent.border.color = "#cbd5e1"
                                    }
                                }
                                onExited: {
                                    parent.scale = 1.0
                                    if (!isSelected) {
                                        parent.border.color = "#e5e7eb"
                                    }
                                }

                                onClicked: {
                                    // 1. 直接切换本地布尔属性，确保界面立即响应
                                    card.isSelected = !card.isSelected
                                    
                                    // 2. 将状态同步回底层数据对象
                                    modelData.selected = card.isSelected
                                    
                                    // 3. 更新全局计数器
                                    selectedUserCount = selectedCount()
                                    
                                    console.log("Card toggled for: " + modelData.username + ", now: " + card.isSelected)
                                }
                            }

                            // 添加点击时的微弱下沉效果
                            transform: Translate {
                                y: mouseArea.pressed ? 2 : 0
                                Behavior on y { NumberAnimation { duration: 50 } }
                            }

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

                // 已选成员头像堆叠
                RowLayout {
                    spacing: 0

                    Repeater {
                        model: Math.min(selectedUserCount, 2)  // 使用计数器

                        Rectangle {
                            width: 44
                            height: 44
                            radius: 22
                            color: Theme.bgAvatar
                            border.width: 4
                            border.color: "#fafafa"
                            z: 10 - index

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

                    // +N 指示器
                    Rectangle {
                        visible: selectedUserCount > 2  // 使用计数器
                        width: 44
                        height: 44
                        radius: 22
                        color: Theme.bgInputArea
                        border.width: 4
                        border.color: "#fafafa"
                        z: 8

                        Label {
                            anchors.centerIn: parent
                            text: "+" + (selectedUserCount - 2)  // 使用计数器
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

                // 文字信息
                ColumnLayout {
                    spacing: 2

                    Label {
                        text: selectedUserCount + " Members Selected"  // 使用计数器
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

                Item { Layout.fillWidth: true }

                // 按钮组
                RowLayout {
                    spacing: 16

                    // Cancel 按钮
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

                    // Create 按钮
                    Button {
                        Layout.preferredWidth: 140
                        Layout.preferredHeight: 48
                        enabled: groupNameInput.text.trim().length > 0 && selectedUserCount > 0  // 使用计数器
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
                                reset()
                            }
                        }
                    }
                }
            }
        }
    }

    // 辅助函数
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

    function reset() {
        groupNameInput.clear()
        searchInput.clear()
        for (var i = 0; i < onlineUsers.length; i++) {
            onlineUsers[i].selected = false
        }
        selectedUserCount = 0  // 重置计数器
    }

    onRejected: {
        reset()
    }
}
