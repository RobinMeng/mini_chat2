# UI 文件说明

本目录存放 Qt Designer 设计的 `.ui` 文件。

## 文件列表

- `main_window.ui` - 主窗口界面

## 使用流程

### 1. 设计界面

使用 Qt Designer 打开 `.ui` 文件进行可视化设计：

```bash
designer ui/main_window.ui
```

### 2. 编译 UI 文件

设计完成后，运行编译脚本将 `.ui` 文件转换为 Python 代码：

```bash
python scripts/compile_ui.py
```

生成的 Python 文件将位于 `src/ui/generated/` 目录下。

### 3. 使用生成的 UI

在业务逻辑代码中继承生成的 UI 类：

```python
from PyQt5.QtWidgets import QMainWindow
from src.ui.generated.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 加载 UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 绑定事件
        self.ui.sendBtn.clicked.connect(self.on_send)
```

## 控件命名规范

为了便于在代码中使用，建议遵循以下命名规范：

- **QListWidget**: `xxxList` (如 `userList`)
- **QTextEdit**: `xxxEdit` / `xxxDisplay` (如 `messageInput`, `messageDisplay`)
- **QPushButton**: `xxxBtn` (如 `sendBtn`, `sendFileBtn`)
- **QLabel**: `xxxLabel` / `xxxTitle` (如 `chatTitle`)

## 注意事项

1. ✅ `.ui` 文件由 Qt Designer 生成，不要手动编辑 XML
2. ✅ 修改 `.ui` 文件后需要重新编译
3. ✅ 生成的 Python 文件位于 `src/ui/generated/` 目录，不要直接修改
4. ✅ 业务逻辑代码放在 `src/ui/main_window.py` 等文件中
5. ✅ 界面设计与业务逻辑完全分离

## 优势

- 🎨 可视化设计界面，直观方便
- 🔧 界面和逻辑分离，易于维护
- 👥 设计师和程序员可以并行工作
- 🔄 界面修改不影响业务逻辑代码
