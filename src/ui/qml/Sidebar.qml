import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// 左侧边栏组件
Rectangle {
    Layout.fillHeight: true
    Layout.preferredWidth: Theme.sidebarWidth
    color: Theme.bgWhite
    border.color: Theme.borderLight

    property string currentUserName: ""
    property var fontAwesomeFamily: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: Theme.spacingLarge
        anchors.bottomMargin: Theme.spacingXLarge
        spacing: Theme.spacingXXLarge

        // 窗口控制按钮
        WindowControlButtons {}

        // Logo
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

        // 导航图标（保留但移除点击事件）
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
                    font.family: fontAwesomeFamily
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

        // 当前用户头像
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: Theme.avatarMedium
            height: Theme.avatarMedium
            radius: Theme.radiusLarge
            color: Theme.bgAvatar
            
            Text {
                text: currentUserName.charAt(0)
                anchors.centerIn: parent
                font.bold: true
            }
        }
    }
}
