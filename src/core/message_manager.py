"""
消息管理器
"""
import time
import traceback
import uuid
from typing import List, Dict, Optional, Callable
from src.core.models import Message
from src.utils.logger import get_logger


logger = get_logger(__name__)


class MessageManager:
    """消息管理器类"""
    
    def __init__(self):
        """初始化消息管理器"""
        self.messages: Dict[str, Message] = {}  # msg_id -> Message
        self.user_messages: Dict[str, List[str]] = {}  # user_id -> [msg_ids]
        self.on_message_received: Optional[Callable] = None
        
    def send_message(self, message: Message) -> bool:
        """
        发送消息
        
        Args:
            message: 消息对象
        
        Returns:
            是否成功
        """
        try:
            # 保存消息
            self.messages[message.msg_id] = message
            
            # 添加到用户消息列表
            if message.to_user_id not in self.user_messages:
                self.user_messages[message.to_user_id] = []
            self.user_messages[message.to_user_id].append(message.msg_id)
            
            logger.info(f"消息已发送: {message.msg_id}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {traceback.format_exc()}")
            return False
    
    def receive_message(self, message: Message) -> bool:
        """
        接收消息
        
        Args:
            message: 消息对象
        
        Returns:
            是否成功
        """
        try:
            # 保存消息
            self.messages[message.msg_id] = message
            
            # 添加到用户消息列表
            if message.from_user_id not in self.user_messages:
                self.user_messages[message.from_user_id] = []
            self.user_messages[message.from_user_id].append(message.msg_id)
            
            # 触发回调
            if self.on_message_received:
                self.on_message_received(message)
            
            logger.info(f"消息已接收: {message.msg_id}")
            return True
            
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return False
    
    def get_message(self, msg_id: str) -> Optional[Message]:
        """
        获取消息
        
        Args:
            msg_id: 消息 ID
        
        Returns:
            消息对象，不存在返回 None
        """
        return self.messages.get(msg_id)
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Message]:
        """
        获取与指定用户的聊天历史
        
        Args:
            user_id: 用户 ID
            limit: 消息数量限制
        
        Returns:
            消息列表
        """
        msg_ids = self.user_messages.get(user_id, [])
        messages = [self.messages[msg_id] for msg_id in msg_ids if msg_id in self.messages]
        
        # 按时间戳排序
        messages.sort(key=lambda m: m.timestamp)
        
        # 限制数量
        if len(messages) > limit:
            messages = messages[-limit:]
        
        return messages
    
    def mark_as_read(self, msg_id: str) -> bool:
        """
        标记消息为已读
        
        Args:
            msg_id: 消息 ID
        
        Returns:
            是否成功
        """
        message = self.messages.get(msg_id)
        if message:
            message.is_read = True
            message.status = "read"
            return True
        return False
    
    def get_unread_count(self, user_id: str) -> int:
        """
        获取与指定用户的未读消息数量
        
        Args:
            user_id: 用户 ID
        
        Returns:
            未读消息数量
        """
        msg_ids = self.user_messages.get(user_id, [])
        unread_count = sum(
            1 for msg_id in msg_ids
            if msg_id in self.messages and not self.messages[msg_id].is_read
        )
        return unread_count
    
    @staticmethod
    def create_message(from_user_id: str, from_username: str,
                      to_user_id: str, to_username: str,
                      content: str, msg_type: str = "TEXT") -> Message:
        """
        创建消息对象
        
        Args:
            from_user_id: 发送者 ID
            from_username: 发送者昵称
            to_user_id: 接收者 ID
            to_username: 接收者昵称
            content: 消息内容
            msg_type: 消息类型
        
        Returns:
            消息对象
        """
        msg_id = f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        return Message(
            msg_id=msg_id,
            type=msg_type,
            from_user_id=from_user_id,
            from_username=from_username,
            to_user_id=to_user_id,
            to_username=to_username,
            content=content,
            timestamp=int(time.time())
        )
