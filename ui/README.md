# UI 文件说明 (QML 版本)

本目录原本存放 `.ui` 文件，现已切换为 **QML** 架构。新的 UI 文件存放于 `src/ui/qml/` 目录下。

## 目录结构

- `src/ui/qml/` - 存放所有 `.qml` 视图文件。
- `src/ui/backend.py` - 存放 QML 后端桥接逻辑 (Controller)。

## 开发流程

### 1. 修改界面

直接编辑 `src/ui/qml/` 目录下的 `.qml` 文件。QML 支持热加载且语法更加现代。

### 2. 交互逻辑

在 `src/ui/backend.py` 中定义属性 (`@pyqtProperty`)、信号 (`pyqtSignal`) 和槽函数 (`@pyqtSlot`)。

### 3. MVC 架构

- **Model**: `src/core/` 下的业务模型。
- **View**: `src/ui/qml/` 下的 QML 文件。
- **Controller**: `src/ui/backend.py` 中的桥接类。

## 优势

- 🚀 性能更佳，渲染更流畅。
- 🎨 声明式语法，UI 开发更快速。
- 🔧 真正的界面与逻辑分离。
