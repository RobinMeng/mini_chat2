"""  
用户管理器（重构版）
直接使用数据库作为单一数据源，不再维护内存字典
"""
import hashlib
import socket
import uuid
import time
from typing import List, Optional
from src.core.models import User
from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserManager:
    """用户管理器类（基于数据库）"""

    def __init__(self, db_manager=None):
        """
        初始化用户管理器
        
        Args:
            db_manager: 数据库管理器实例，如为 None 则延迟注入
        """
        self.db_manager = db_manager
        self.current_user: Optional[User] = None

    def set_db_manager(self, db_manager):
        """设置数据库管理器（用于延迟注入）"""
        self.db_manager = db_manager

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
        # username uuid随机生成
        username = "User:" + uuid.uuid4().hex[:8]

        if not username:
            username = hostname

        self.current_user = User(
            user_id=user_id,
            username=username,
            hostname=hostname,
            ip_address=self._get_local_ip(),
            tcp_port=config.TCP_PORT,
            status="online"
        )

        # 将当前用户保存到数据库
        if self.db_manager:
            self._save_user_to_db(self.current_user)

        logger.info(f"当前用户已初始化: {self.current_user.username} ({self.current_user.user_id})")
        return self.current_user

    def add_user(self, user: User) -> bool:
        """
        添加或更新用户（直接写入数据库）
        
        Args:
            user: 用户对象
        
        Returns:
            是否成功
        """
        try:
            # 不添加自己
            if self.current_user and user.user_id == self.current_user.user_id:
                return False

            # 检查是否已存在
            existing_user = self.get_user(user.user_id)
            is_new = existing_user is None

            # 保存或更新到数据库
            self._save_user_to_db(user)

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
        移除用户（从数据库删除）
        
        Args:
            user_id: 用户 ID
        
        Returns:
            是否成功
        """
        try:
            if not self.db_manager:
                return False

            user = self.get_user(user_id)
            if user:
                sql = "DELETE FROM users WHERE user_id = ?"
                self.db_manager.execute(sql, (user_id,))
                logger.info(f"用户已移除: {user.username} ({user_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"移除用户失败: {e}")
            return False

    def set_user_offline(self, user_id: str) -> bool:
        """
        将用户标记为下线（更新数据库）
        
        Args:
            user_id: 用户 ID
        
        Returns:
            是否成功
        """
        try:
            if not self.db_manager:
                return False

            user = self.get_user(user_id)
            if user:
                sql = "UPDATE users SET status = 'offline', updated_at = ? WHERE user_id = ?"
                self.db_manager.execute(sql, (int(time.time()), user_id))
                logger.info(f"用户已标记为下线: {user.username} ({user_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"标记用户下线失败: {e}")
            return False

    def get_user(self, user_id: str) -> Optional[User]:
        """
        获取用户信息（从数据库查询）
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户对象，不存在返回 None
        """
        try:
            if not self.db_manager:
                return None

            sql = "SELECT * FROM users WHERE user_id = ?"
            result = self.db_manager.query(sql, (user_id,))
            if result:
                return User.from_dict(dict(result[0]))
            return None
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None

    def get_online_users(self) -> List[User]:
        """
        获取所有在线用户（从数据库查询）
        
        Returns:
            在线用户列表
        """
        try:
            if not self.db_manager:
                return []

            sql = "SELECT * FROM users WHERE status = 'online'"
            results = self.db_manager.query(sql)
            return [User.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"查询在线用户失败: {e}")
            return []

    def get_all_users(self) -> List[User]:
        """
        获取所有用户（从数据库查询）
        
        Returns:
            用户列表
        """
        try:
            if not self.db_manager:
                return []

            sql = "SELECT * FROM users ORDER BY status DESC, username ASC"
            results = self.db_manager.query(sql)
            return [User.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"查询所有用户失败: {e}")
            return []

    def _save_user_to_db(self, user: User):
        """将用户保存到数据库（INSERT OR REPLACE）"""
        if not self.db_manager:
            return

        sql = """
            INSERT OR REPLACE INTO users 
            (user_id, username, hostname, ip_address, tcp_port, status, last_seen, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = int(time.time())
        self.db_manager.execute(sql, (
            user.user_id,
            user.username,
            user.hostname,
            user.ip_address,
            user.tcp_port,
            user.status,
            now,
            now,
            now
        ))

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
            mac_str = ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))

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
