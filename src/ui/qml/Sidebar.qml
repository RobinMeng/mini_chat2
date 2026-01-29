import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// 左侧边栏组件：提供应用导航图标、窗口管理按钮和个人资料入口
Rectangle {
    Layout.fillHeight: true                 // 垂直填满
    Layout.preferredWidth: Theme.sidebarWidth // 侧边栏宽度固定
    color: Theme.bgWhite
    border.color: Theme.borderLight

    property string currentUserName: ""     // 当前登录用户名
    property var fontAwesomeFamily: ""      // 图标字体名称

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: Theme.spacingLarge
        anchors.bottomMargin: Theme.spacingXLarge
        spacing: Theme.spacingXXLarge        // 模块之间的间距

        // 引入独立的窗口控制按钮组件（关闭、最小化等）
        WindowControlButtons {}

        // 应用 Logo 区域
        Rectangle {
            Layout.topMargin: Theme.spacingMedium
            Layout.alignment: Qt.AlignHCenter
            width: Theme.avatarMedium
            height: Theme.avatarMedium
            radius: Theme.radiusLarge
            color: Theme.primary            // 使用品牌主色
            
            Text {
                text: "M"                   // MiniChat 的 M
                color: Theme.textWhite
                anchors.centerIn: parent
                font.bold: true
                font.pixelSize: Theme.fontSizeLogo
            }
        }

        // 导航图标列表：使用 Repeater 根据数组动态生成
        Repeater {
            // 模型数组，包含四个功能图标
            model: [Theme.iconChat, Theme.iconGroup, Theme.iconFolder, Theme.iconSettings]
            
            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: Theme.buttonMedium
                height: Theme.buttonMedium
                radius: Theme.radiusLarge
                // 背景色逻辑：第一个图标（聊天）默认激活，其他图标在鼠标悬停时变色
                color: index === 0 ? Theme.bgHover : (iconMouseArea.containsMouse ? Theme.bgHover : Theme.bgTransparent)
                // 缩放效果：悬停时轻微放大
                scale: iconMouseArea.containsMouse ? 1.05 : 1.0
                Behavior on color { ColorAnimation { duration: 150 } }
                Behavior on scale { NumberAnimation { duration: 100 } }
                
                Text {
                    anchors.centerIn: parent
                    text: modelData          // 对应 model 数组中的图标字符
                    font.family: fontAwesomeFamily
                    font.pixelSize: Theme.iconSizeMedium
                    // 颜色逻辑：激活项用主色，普通项用灰色
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

        // 占位符：占据所有剩余垂直空间，将个人头像推到底部
        Item { Layout.fillHeight: true }

        // 当前用户头像区域
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: Theme.avatarMedium
            height: Theme.avatarMedium
            radius: Theme.radiusLarge
            color: Theme.bgAvatar
            
            Text {
                // 显示用户名的首字符
                text: currentUserName.charAt(0)
                anchors.centerIn: parent
                font.bold: true
            }
        }
    }
}
