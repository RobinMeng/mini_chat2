import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// 窗口控制按钮组件（关闭、最小化、最大化）
Rectangle {
    Layout.fillWidth: true
    Layout.preferredHeight: 30
    color: "transparent"
    z: 2

    RowLayout {
        anchors.centerIn: parent
        spacing: 8

        // 关闭按钮
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

        // 最小化按钮
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

        // 最大化按钮
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
                onClicked: {
                    if (window.visibility === Window.Maximized) {
                        window.showNormal()
                    } else {
                        window.showMaximized()
                    }
                }
                cursorShape: Qt.PointingHandCursor
            }
        }
    }
}
