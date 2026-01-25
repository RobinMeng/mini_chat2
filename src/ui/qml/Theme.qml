pragma Singleton
import QtQuick 2.15

QtObject {
    // === 主题色彩系统 ===
    readonly property color primary: "#3b82f6"
    readonly property color charcoal: "#1a1a1a"
    readonly property color sidebarBg: "#f9fafb"
    readonly property color sentBubble: "#f0f7ff"
    readonly property color receivedBubble: "#ffffff"
    readonly property color online: "#10b981"
    readonly property color offline: "#94a3b8"
    readonly property color unreadBadge: "#ff4d4f"

    // === 窗口控制按钮颜色 ===
    readonly property color windowClose: "#ff5f56"
    readonly property color windowMinimize: "#ffbd2e"
    readonly property color windowMaximize: "#27c93f"

    // === 边框与分隔线 ===
    readonly property color borderLight: "#f0f0f0"
    readonly property color borderGray: "#e5e7eb"
    readonly property color borderActive: "#e5e7eb"

    // === 文字颜色 ===
    readonly property color textPrimary: charcoal
    readonly property color textSecondary: "#94a3b8"
    readonly property color textPlaceholder: "#94a3b8"
    readonly property color textWhite: "white"

    // === 背景颜色 ===
    readonly property color bgWhite: "white"
    readonly property color bgTransparent: "transparent"
    readonly property color bgInputArea: "#f8fafc"
    readonly property color bgAvatar: "#e2e8f0"
    readonly property color bgHover: "#f0f7ff"

    // === 尺寸规范 ===
    readonly property int windowWidth: 1000
    readonly property int windowHeight: 700
    readonly property int sidebarWidth: 70
    readonly property int contactListWidth: 280
    readonly property int headerHeight: 75
    readonly property int inputAreaHeight: 90

    // === 间距规范 ===
    readonly property int spacingSmall: 5
    readonly property int spacingMedium: 10
    readonly property int spacingLarge: 15
    readonly property int spacingXLarge: 20
    readonly property int spacingXXLarge: 25

    // === 圆角规范 ===
    readonly property int radiusSmall: 6
    readonly property int radiusMedium: 10
    readonly property int radiusLarge: 12
    readonly property int radiusXLarge: 15
    readonly property int radiusBubble: 18
    readonly property int radiusWindow: 12

    // === 字体规范 ===
    readonly property int fontSizeSmall: 10
    readonly property int fontSizeMedium: 11
    readonly property int fontSizeNormal: 14
    readonly property int fontSizeLarge: 16
    readonly property int fontSizeXLarge: 18
    readonly property int fontSizeTitle: 20
    readonly property int fontSizeLogo: 20

    // === 头像与图标尺寸 ===
    readonly property int avatarSmall: 35
    readonly property int avatarMedium: 40
    readonly property int avatarLarge: 45
    readonly property int iconSizeSmall: 12
    readonly property int iconSizeMedium: 18
    readonly property int iconSizeLarge: 20

    // === 用户列表项 ===
    readonly property int userItemHeight: 70
    readonly property int searchBoxHeight: 40

    // === 按钮尺寸 ===
    readonly property int buttonSmall: 40
    readonly property int buttonMedium: 45

    // === 边框宽度 ===
    readonly property int borderWidthThin: 1
    readonly property int borderWidthMedium: 2

    // === FontAwesome 图标编码 ===
    readonly property string iconChat: "\uf075"
    readonly property string iconGroup: "\uf0c0"
    readonly property string iconFolder: "\uf07b"
    readonly property string iconSettings: "\uf013"
    readonly property string iconPhone: "\uf095"
    readonly property string iconVideo: "\uf03d"
    readonly property string iconMore: "\uf142"
    readonly property string iconSend: "\uf1d8"
}
