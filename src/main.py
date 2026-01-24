"""
主程序入口
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from src.config import config
from src.ui.backend import QmlBackend
from src.utils.logger import setup_logger


def main():
    """主函数"""
    # 初始化配置目录
    config.init_dirs()
    
    # 初始化日志
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info(f"{config.APP_NAME} v{config.APP_VERSION} 启动中...")
    logger.info("=" * 60)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    
    # 创建 QML 引擎
    engine = QQmlApplicationEngine()
    
    # 创建后端桥接对象
    backend = QmlBackend()
    
    # 注入后端对象到 QML 上下文
    engine.rootContext().setContextProperty("backend", backend)
    
    # 加载主界面
    qml_file = Path(__file__).parent / "ui" / "qml" / "MainWindow.qml"
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        logger.error("加载 QML 失败")
        sys.exit(-1)
    
    logger.info("应用程序 (QML) 启动完成")
    
    # 运行应用
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
