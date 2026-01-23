# MiniChat - 局域网即时通讯工具

一个基于 Python 和 PyQt5 的局域网聊天工具，无需登录，自动发现局域网内的其他用户并进行实时通讯。

## 功能特性

- ✅ 无需登录，自动识别用户
- ✅ 局域网内自动发现在线用户（UDP 广播）
- ✅ 实时消息传输（TCP 点对点）
- ✅ 一对一聊天
- ✅ 聊天历史记录
- ✅ 图形化界面
- 🚧 群组聊天（开发中）
- 🚧 文件传输（开发中）

## 技术栈

- **Python 3.8+**
- **PyQt5** - GUI 框架
- **socket + selectors** - 高性能 I/O 多路复用网络通信
- **SQLite** - 本地数据存储
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

### 修改界面

1. 使用 Qt Designer 打开 UI 文件：
```bash
designer ui/main_window.ui
```

2. 设计完成后，编译 UI 文件：
```bash
python scripts/compile_ui.py
```

3. 重新运行程序查看效果

### 项目特点

- ✅ **界面与逻辑分离**: `.ui` 文件定义界面，Python 代码实现逻辑
- ✅ **可视化设计**: 使用 Qt Designer 可视化设计界面
- ✅ **高性能网络**: 基于 `selectors` 实现 I/O 多路复用，单线程支持高并发连接
- ✅ **健壮的协议**: 采用 4 字节长度前缀 + JSON 协议，解决 TCP 粘包/半包问题
- ✅ **易于维护**: 核心网络能力收拢在 `network_utils`，界面修改不影响业务逻辑

## 配置说明

配置文件位于 `src/config.py`，可以修改以下参数：

- `BROADCAST_PORT`: UDP 广播端口（默认 9999）
- `TCP_PORT`: TCP 消息端口（默认 10000）
- `BROADCAST_INTERVAL`: 心跳间隔（默认 5 秒）
- `MAX_FILE_SIZE`: 最大文件大小（默认 100MB）

## 开发进度

### 已完成 ✅
- [x] 项目结构搭建
- [x] 基础配置管理
- [x] 日志系统
- [x] 数据库设计与实现
- [x] UDP 广播服务实现
- [x] TCP 消息服务实现
- [x] 用户管理功能
- [x] 消息管理功能
- [x] 主窗口设计与实现
- [x] 用户列表显示
- [x] 聊天消息显示
- [x] 消息发送功能

### 开发中 🚧
- [ ] 文件传输功能
- [ ] 群组聊天功能
- [ ] 系统托盘功能
- [ ] 表情选择器
- [ ] 消息通知

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
