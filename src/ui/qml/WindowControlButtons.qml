import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// 窗口控制按钮组件：模拟 macOS 风格的三个圆形功能按钮（关闭、最小化、最大化）
Rectangle {
    Layout.fillWidth: true                  // 填满侧边栏顶部宽度
    Layout.preferredHeight: 30              // 固定高度
    color: "transparent"
    z: 2                                    // 确保在最上层，避免被拖拽 MouseArea 阻挡

    RowLayout {
        anchors.centerIn: parent            // 居中排列
        spacing: 8                          // 按钮之间的间距

        // 1. 关闭按钮 (红色)
        Rectangle {
            width: Theme.iconSizeSmall
            height: Theme.iconSizeSmall
            radius: Theme.radiusSmall       // 正圆
            color: Theme.windowClose
            // 悬停缩放动画
            scale: closeMouseArea.containsMouse ? 1.1 : 1.0
            Behavior on scale { NumberAnimation { duration: 100 } }
            
            Text {
                anchors.centerIn: parent
                text: "×"                   // 悬停时显示的 X 符号
                color: "#5a0000"
                font.pixelSize: 10
                font.bold: true
                visible: closeMouseArea.containsMouse
            }
            
            MouseArea {
                id: closeMouseArea
                anchors.fill: parent
                hoverEnabled: true          // 开启悬停监测
                onClicked: window.close()   // 触发窗口关闭
                cursorShape: Qt.PointingHandCursor
            }
        }

        // 2. 最小化按钮 (黄色)
        Rectangle {
            width: Theme.iconSizeSmall
            height: Theme.iconSizeSmall
            radius: Theme.radiusSmall
            color: Theme.windowMinimize
            scale: minimizeMouseArea.containsMouse ? 1.1 : 1.0
            Behavior on scale { NumberAnimation { duration: 100 } }
            
            Text {
                anchors.centerIn: parent
                text: "−"                   // 悬停时显示的减号符号
                color: "#855a00"
                font.pixelSize: 10
                font.bold: true
                visible: minimizeMouseArea.containsMouse
            }
            
            MouseArea {
                id: minimizeMouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: window.showMinimized() // 最小化到任务栏
                cursorShape: Qt.PointingHandCursor
            }
        }

        // 3. 全屏/最大化按钮 (绿色)
        Rectangle {
            width: Theme.iconSizeSmall
            height: Theme.iconSizeSmall
            radius: Theme.radiusSmall
            color: Theme.windowMaximize
            scale: maximizeMouseArea.containsMouse ? 1.1 : 1.0
            Behavior on scale { NumberAnimation { duration: 100 } }
            
            Text {
                anchors.centerIn: parent
                text: "＋"                   // 悬停时显示的加号符号
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
                    // 切换最大化与常规窗口状态
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
