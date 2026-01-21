"""
用户管理器
"""
import hashlib
import socket
import uuid
from typing import Dict, List, Optional
from src.core.models import User
from src.config import config
from src.utils.logger import get_logger


logger = get_logger(__name__)


class UserManager:
    """用户管理器类"""
    
    def __init__(self):
        """初始化用户管理器"""
        self.users: Dict[str, User] = {}  # user_id -> User
        self.current_user: Optional[User] = None
        
    def initialize_current_user(self, username: str = "") -> User:
        """
        初始化当前用户
        
        Args:
            username: 用户昵称，留空使用主机名
        
        Returns:
            当前用户对象
        """
        user_id = self._generate_user_id()
        hostname = socket.gethostname()
        
        if not username:
            username = hostname
        
        self.current_user = User(
            user_id=user_id,
            username=username,
            hostname=hostname,
            ip_address=self._get_local_ip(),
            tcp_port=config.TCP_PORT
        )
        
        logger.info(f"当前用户已初始化: {self.current_user.username} ({self.current_user.user_id})")
        return self.current_user
    
    def add_user(self, user: User) -> bool:
        """
        添加或更新用户
        
        Args:
            user: 用户对象
        
        Returns:
            是否成功
        """
        try:
            # 不添加自己
            if self.current_user and user.user_id == self.current_user.user_id:
                return False
            
            is_new = user.user_id not in self.users
            self.users[user.user_id] = user
            
            if is_new:
                logger.info(f"新用户加入: {user.username} ({user.user_id})")
            else:
                logger.debug(f"用户信息已更新: {user.username}")
            
            return True
            
        except Exception as e:
            logger.error(f"添加用户失败: {e}")
            return False
    
    def remove_user(self, user_id: str) -> bool:
        """
        移除用户
        
        Args:
            user_id: 用户 ID
        
        Returns:
            是否成功
        """
        try:
            if user_id in self.users:
                user = self.users.pop(user_id)
                logger.info(f"用户已移除: {user.username} ({user_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"移除用户失败: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户对象，不存在返回 None
        """
        return self.users.get(user_id)
    
    def get_online_users(self) -> List[User]:
        """
        获取所有在线用户
        
        Returns:
            在线用户列表
        """
        return [user for user in self.users.values() if user.status == "online"]
    
    def get_all_users(self) -> List[User]:
        """
        获取所有用户
        
        Returns:
            用户列表
        """
        return list(self.users.values())
    
    @staticmethod
    def _generate_user_id() -> str:
        """
        生成用户唯一 ID
        基于 MAC 地址 + UUID
        
        Returns:
            用户 ID
        """
        try:
            # 获取 MAC 地址
            mac = uuid.getnode()
            mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            
            # 使用 MAC 地址 + 随机 UUID 生成唯一 ID
            unique_string = f"{mac_str}_{uuid.uuid4()}"
            user_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
            
            return user_id
            
        except Exception as e:
            logger.error(f"生成用户 ID 失败: {e}")
            # 如果失败，使用随机 UUID
            return uuid.uuid4().hex[:16]
    
    @staticmethod
    def _get_local_ip() -> str:
        """
        获取本机 IP 地址
        
        Returns:
            IP 地址字符串
        """
        try:
            # 创建一个临时 socket 连接获取本机 IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.error(f"获取本机 IP 失败: {e}")
            return "127.0.0.1"
