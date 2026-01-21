"""
数据模型定义
"""
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class User:
    """用户数据模型"""
    user_id: str
    username: str
    hostname: str = ""
    ip_address: str = ""
    tcp_port: int = 10000
    status: str = "online"  # online/offline
    last_seen: int = field(default_factory=lambda: int(time.time()))
    avatar: str = ""
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'tcp_port': self.tcp_port,
            'status': self.status,
            'last_seen': self.last_seen,
            'avatar': self.avatar
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建"""
        return cls(**data)


@dataclass
class Message:
    """消息数据模型"""
    msg_id: str
    type: str = "TEXT"  # TEXT/FILE/IMAGE
    from_user_id: str = ""
    from_username: str = ""
    to_user_id: str = ""
    to_username: str = ""
    content: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time()))
    is_group: bool = False
    group_id: Optional[str] = None
    is_read: bool = False
    status: str = "sending"  # sending/sent/received/read/failed
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'msg_id': self.msg_id,
            'type': self.type,
            'from_user_id': self.from_user_id,
            'from_username': self.from_username,
            'to_user_id': self.to_user_id,
            'to_username': self.to_username,
            'content': self.content,
            'timestamp': self.timestamp,
            'is_group': self.is_group,
            'group_id': self.group_id,
            'is_read': self.is_read,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """从字典创建"""
        return cls(**data)


@dataclass
class FileTransfer:
    """文件传输数据模型"""
    file_id: str
    from_user_id: str = ""
    to_user_id: str = ""
    filename: str = ""
    filesize: int = 0
    file_type: str = ""
    checksum: str = ""
    save_path: str = ""
    chunk_size: int = 4096
    total_chunks: int = 0
    transferred_chunks: int = 0
    status: str = "pending"  # pending/transferring/completed/failed
    progress: float = 0.0  # 0-100
    start_time: int = 0
    end_time: int = 0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'file_id': self.file_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'filename': self.filename,
            'filesize': self.filesize,
            'file_type': self.file_type,
            'checksum': self.checksum,
            'save_path': self.save_path,
            'chunk_size': self.chunk_size,
            'total_chunks': self.total_chunks,
            'transferred_chunks': self.transferred_chunks,
            'status': self.status,
            'progress': self.progress,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileTransfer':
        """从字典创建"""
        return cls(**data)
