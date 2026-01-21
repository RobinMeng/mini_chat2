"""
文件传输服务
"""
import os
import hashlib
from pathlib import Path
from typing import Callable, Optional
from src.config import config
from src.utils.logger import get_logger


logger = get_logger(__name__)


class FileTransferService:
    """文件传输服务类"""
    
    def __init__(self):
        """初始化文件传输服务"""
        self.active_transfers = {}  # 活动的传输任务
    
    def send_file(self, file_path: str, target_ip: str, target_port: int,
                  on_progress: Optional[Callable] = None) -> bool:
        """
        发送文件
        
        Args:
            file_path: 文件路径
            target_ip: 目标 IP
            target_port: 目标端口
            on_progress: 进度回调函数
        
        Returns:
            是否发送成功
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return False
            
            file_size = file_path.stat().st_size
            
            if file_size > config.MAX_FILE_SIZE:
                logger.error(f"文件太大: {file_size} bytes")
                return False
            
            # TODO: 实现文件发送逻辑
            logger.info(f"准备发送文件: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"发送文件失败: {e}")
            return False
    
    def receive_file(self, file_id: str, save_path: str,
                     on_progress: Optional[Callable] = None) -> bool:
        """
        接收文件
        
        Args:
            file_id: 文件传输 ID
            save_path: 保存路径
            on_progress: 进度回调函数
        
        Returns:
            是否接收成功
        """
        try:
            # TODO: 实现文件接收逻辑
            logger.info(f"准备接收文件: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"接收文件失败: {e}")
            return False
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """
        计算文件 MD5 校验和
        
        Args:
            file_path: 文件路径
        
        Returns:
            MD5 校验和
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(config.CHUNK_SIZE), b''):
                md5.update(chunk)
        return md5.hexdigest()
