# MiniChat - 局域网即时通讯工具

一个基于 Python 和 PyQt5 的局域网聊天工具，无需登录，自动发现局域网内的其他用户并进行实时通讯。

## 功能特性

- ✅ 无需登录，自动识别用户
- ✅ 局域网内自动发现在线用户（UDP 广播）
- ✅ 实时消息传输（TCP 点对点）
- ✅ **未读提醒**: 实时显示每个联系人的未读消息数量
- ✅ **下线感知**: 用户退出立即通知好友，实时更新列表状态并禁用发送
- ✅ **视觉升级**: 基于 FontAwesome 的精致图标与 macOS 风格无边框设计
- ✅ **阅后即焚**: 退出程序物理销毁 SQLite 数据库，实现真正的“无痕运行”
- ✅ 图形化界面（基于 QML 现代架构，支持高性能列表渲染）
- 🚧 群组聊天（开发中）
- 🚧 文件传输（开发中）

## 技术栈

- **Python 3.8+**
- **PyQt5** - GUI 框架
- **socket + selectors** - 高性能 I/O 多路复用网络通信
- **SQLite (临时)** - 运行时数据缓冲（退出即焚）
- **threading** - 多线程处理

## 项目结构

```
mini_chat2/
├── docs/                    # 设计文档
├── src/                     # 源代码
│   ├── network/            # 网络通信模块
│   ├── core/               # 核心业务逻辑
│   ├── ui/                 # 界面模块
│   ├── database/           # 数据库模块
│   └── utils/              # 工具类
├── resources/               # 资源文件
├── scripts/                 # 工具脚本
├── tests/                   # 测试代码
└── run.py                   # 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python run.py
```

### 3. 测试网络功能

```bash
# 测试 UDP 广播服务
python tests/test_network_simple.py broadcast

# 测试 TCP 消息服务
python tests/test_network_simple.py message
```

## 开发说明

### 架构模式
项目采用 **MVC (Model-View-Controller)** 架构：
- **View (QML)**: 负责界面展示与声明式交互。
- **Controller (Python Backend)**: 通过 `QObject` 桥接，暴露属性与槽函数供 QML 调用。
- **Model**: Python 侧实现的 `MessageListModel` (继承自 `QAbstractListModel`) 驱动界面高效刷新。

### 修改界面
1. 直接编辑 `src/ui/qml/` 目录下的 `.qml` 文件。
2. 重新运行 `python run.py` 即可查看效果（无需编译）。

### 项目特点
- ✅ **极致视觉**: 采用三栏式现代布局，支持 FontAwesome 矢量图标动态加载。
- ✅ **无边框窗口**: 沉浸式 UI 体验，支持原生窗口拖拽与 macOS 风格控制。
- ✅ **数据驱动**: 使用 `QAbstractListModel` 驱动界面，解决大数据量下的卡顿与绑定失效问题。
- ✅ **单机多实例测试**: 引入 `SO_REUSEPORT`，支持同一台机器开启多个客户端进行互通测试。
- ✅ **后端重构**: 采用复合控制器模式，将业务逻辑解耦为独立子模块，提升系统可维护性。
- ✅ **数据库单一数据源**: UserManager 和 MessageListModel 均采用数据库直查架构，彻底消除内存与数据库双重维护问题。
- ✅ **隐私安全**: 严格的"阅后即焚"逻辑，物理层级确保数据不留存。
- ✅ **健壮的协议**: 采用 4 字节长度前缀 + JSON 协议，解决 TCP 粘包/半包问题。

## 配置说明

配置文件位于 `src/config.py`，可以修改以下参数：

- `BROADCAST_PORT`: UDP 广播端口（默认 9999）
- `TCP_PORT`: TCP 消息端口（默认 10000）
- `BROADCAST_INTERVAL`: 心跳间隔（默认 5 秒）
- `MAX_FILE_SIZE`: 最大文件大小（默认 100MB）

## 开发进度

### 已完成 ✅
- [x] 项目结构搭建与 QML 基础架构
- [x] 后端控制器解耦 (UserController/ChatController/GroupController)
- [x] **数据库单一数据源架构**: MessageListModel 和 UserManager 完全基于数据库查询
- [x] 基于 Python 的 `QAbstractListModel` 列表驱动
- [x] UDP 广播服务（支持 `SO_REUSEPORT` 单机多开）
- [x] TCP 异步消息收发与粘包处理
- [x] 群组邀请同步与组播去重逻辑
- [x] **阅后即焚** 数据库销毁逻辑
- [x] **未读消息计数** 与红色气泡提醒
- [x] **下线状态感知** 与发送功能自动锁定
- [x] **UI 样式解耦**: Theme.qml 集中管理所有颜色配置
- [x] 环境变量驱动的端口与数据路径配置

### 开发中 🚧
- [ ] 文件传输功能
- [ ] 系统托盘功能
- [ ] 表情选择器

## 文档

详细设计文档请参考：

- [设计文档](docs/设计文档.md)
- [开发计划](docs/开发计划.md)
- [技术规格说明](docs/技术规格说明.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

Robin Meng
