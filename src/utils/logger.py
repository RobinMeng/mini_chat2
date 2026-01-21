"""
日志工具模块
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config import config


def setup_logger() -> logging.Logger:
    """
    设置并初始化日志系统
    
    Returns:
        根日志记录器
    """
    # 确保日志目录存在
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 创建文件处理器（带日志轮转）
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
    
    Returns:
        日志记录器
    """
    return logging.getLogger(name)
