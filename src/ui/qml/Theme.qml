pragma Singleton              // 声明为单例模式，在其他 QML 文件中直接通过 Theme.xxx 访问
import QtQuick 2.15

// 主题配置文件：集中管理全局的颜色、尺寸、字体和图标
QtObject {
    // === 主题色彩系统 ===
    readonly property color primary: "#3b82f6"       // 品牌主色调（蓝色）
    readonly property color charcoal: "#1a1a1a"      // 深炭灰色
    readonly property color sidebarBg: "#f9fafb"     // 侧边栏背景（浅灰白）
    readonly property color sentBubble: "#f0f7ff"    // 发送消息气泡背景
    readonly property color receivedBubble: "#ffffff" // 接收消息气泡背景
    readonly property color online: "#10b981"        // 在线状态颜色（绿色）
    readonly property color groupOnline: "#10b981"   // 群组在线状态颜色（绿色）
    readonly property color offline: "#94a3b8"       // 离线状态颜色（灰色）
    readonly property color unreadBadge: "#ff4d4f"   // 未读消息提醒色（红色）

    // === 窗口控制按钮颜色 (macOS 风格) ===
    readonly property color windowClose: "#ff5f56"    // 关闭
    readonly property color windowMinimize: "#ffbd2e" // 最小化
    readonly property color windowMaximize: "#27c93f" // 最大化

    // === 边框与分隔线 ===
    readonly property color borderLight: "#f0f0f0"   // 极淡边框
    readonly property color borderGray: "#e5e7eb"    // 标准灰色边框
    readonly property color separator: "#333333"     // 分割线颜色（灰黑色）
    readonly property color separatorLight: "#d1d5db" // 浅灰色分割线
    readonly property color borderActive: "#e5e7eb"  // 激活项边框

    // === 文字颜色 ===
    readonly property color textPrimary: charcoal     // 主要文字
    readonly property color textSecondary: "#94a3b8"  // 次要文字/辅助说明
    readonly property color textPlaceholder: "#94a3b8" // 输入框提示文字
    readonly property color textWhite: "white"       // 白色文字
    readonly property color textBlack: "black"       // 黑色文字

    // === 背景颜色 ===
    readonly property color bgWhite: "white"         // 纯白背景
    readonly property color bgTransparent: "transparent" // 透明背景
    readonly property color bgInputArea: "#f8fafc"   // 输入区域背景
    readonly property color bgAvatar: "#e2e8f0"      // 头像默认背景
    readonly property color bgHover: "#f0f7ff"       // 鼠标悬停时的淡蓝色背景

    // === 窗口尺寸规范 ===
    readonly property int windowWidth: 1000
    readonly property int windowHeight: 700
    readonly property int sidebarWidth: 70           // 左侧导航栏宽度
    readonly property int contactListWidth: 280      // 联系人列表宽度
    readonly property int headerHeight: 75           // 顶部标题栏高度
    readonly property int inputAreaHeight: 90        // 底部输入区域高度

    // === 间距规范 (Padding & Margins) ===
    readonly property int spacingSmall: 5
    readonly property int spacingMedium: 10
    readonly property int spacingLarge: 15
    readonly property int spacingXLarge: 20
    readonly property int spacingXXLarge: 25

    // === 圆角规范 (Corner Radius) ===
    readonly property int radiusSmall: 6
    readonly property int radiusMedium: 10
    readonly property int radiusLarge: 12
    readonly property int radiusXLarge: 15
    readonly property int radiusBubble: 18           // 消息气泡圆角
    readonly property int radiusWindow: 12           // 主窗口圆角

    // === 字体大小规范 ===
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

    // === 列表项样式 ===
    readonly property int userItemHeight: 70         // 联系人项高度
    readonly property int searchBoxHeight: 40        // 搜索框高度

    // === 按钮尺寸 ===
    readonly property int buttonSmall: 40
    readonly property int buttonMedium: 45

    // === 边框宽度 ===
    readonly property int borderWidthThin: 1
    readonly property int borderWidthMedium: 2

    // === FontAwesome 图标编码 (Unicode) ===
    readonly property string iconChat: "\uf075"      // 气泡图标
    readonly property string iconGroup: "\uf0c0"     // 多人图标
    readonly property string iconFolder: "\uf07b"    // 文件夹图标
    readonly property string iconSettings: "\uf013"  // 设置图标
    readonly property string iconPhone: "\uf095"     // 电话图标
    readonly property string iconVideo: "\uf03d"     // 视频图标
    readonly property string iconMore: "\uf142"      // 更多图标
    readonly property string iconSend: "\uf1d8"      // 发送/飞机图标
}
