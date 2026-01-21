"""应用程序配置"""
import os
from pathlib import Path


class Config:
    """应用程序配置类"""
    # 应用信息
    APP_NAME = "MiniChat"
    APP_VERSION = "1.0.0"
    
    # 路径配置
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"
    RESOURCE_DIR = BASE_DIR / "resources"
    UI_DIR = BASE_DIR / "ui"
    
    # 网络配置
    BROADCAST_PORT = 9999
    TCP_PORT = 10000
    BROADCAST_INTERVAL = 5  # 秒
    HEARTBEAT_TIMEOUT = 15  # 秒
    USER_REMOVE_TIMEOUT = 30  # 秒
    BROADCAST_ADDRESS = "255.255.255.255"
    
    # 用户配置
    DEFAULT_USERNAME = ""  # 留空使用主机名
    MAX_USERNAME_LENGTH = 20
    
    # 消息配置
    MAX_MESSAGE_LENGTH = 5000
    MESSAGE_HISTORY_LIMIT = 100
    
    # 文件传输配置
    CHUNK_SIZE = 4096  # 4KB
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES = [
        'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
        'jpg', 'jpeg', 'png', 'gif', 'bmp',
        'zip', 'rar', '7z', 'tar', 'gz'
    ]
    
    # 数据库配置
    DB_NAME = "chat.db"
    
    @property
    def DB_PATH(self):
        return self.DATA_DIR / self.DB_NAME
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @property
    def LOG_FILE(self):
        return self.LOG_DIR / "minichat.log"
    
    # UI 配置
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    WINDOW_MIN_WIDTH = 700
    WINDOW_MIN_HEIGHT = 500
    
    # 主题配置
    THEME = "light"  # light/dark
    
    @classmethod
    def init_dirs(cls):
        """初始化必要的目录"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        cls.RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
        cls.UI_DIR.mkdir(exist_ok=True)


# 创建全局配置实例
config = Config()
