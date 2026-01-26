# Bug 修复记录

## 1. 消息无法自动实时加载问题

### 问题描述
在实时聊天过程中，对方发送的消息虽然已被网络模块接收，但 UI 界面（ListView）不会自动显示新消息。必须手动点击好友头像重新加载会话，新消息才会出现。

### 根本原因
1. **跨线程 UI 操作（核心原因）**：消息接收回调 `_on_message_received` 运行在后台网络线程中。在后台线程中直接操作 QML Model（调用 `add_message`）或发射 UI 信号，会导致 Qt 内部事件循环冲突，界面无法感知数据变化。
2. **QML 渲染依赖滚动条**：当消息数量较少、尚未产生滚动条时，ListView 认为可见区域未变化，有时会跳过新增 Item 的渲染。
3. **信号绑定不完整**：最初 MessageListModel 实例未设置 `parent`，导致部分信号无法正确传递给 QML 引擎。

### 修复方案
1. **异步信号机制**：在 `backend.py` 中引入了内部专用信号 `_internalMessageSignal`。
   - 后台线程只负责数据解析和数据库写入。
   - 通过 `_internalMessageSignal.emit(message)` 将数据派发出去。
   - Qt 会通过 `QueuedConnection` 自动将信号转到主线程（UI 线程）执行。
2. **主线程安全处理**：建立 `_ui_safe_process_received_message` 方法，专门在主线程执行 Model 更新和信号发射。
3. **显式刷新信号**：在 Model 插入行（`endInsertRows`）后，额外调用 `dataChanged.emit`，强制 QML 刷新对应行，解决了无滚动条时不渲染的问题。

---