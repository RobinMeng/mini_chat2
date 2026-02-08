from PyQt5.QtCore import QObject, pyqtSignal
from src.core.models import Message
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChatController(QObject):
    """消息与会话业务控制器"""
    newMessageReceived = pyqtSignal(dict)
    newMessageSent = pyqtSignal(dict)
    groupMessageReceived = pyqtSignal(dict)
    
    # 内部跨线程信号由主 Backend 转发至此处处理，或在此处定义
    
    def __init__(self, message_model, db_manager, user_manager, message_service, group_manager, message_manager):
        super().__init__()
        self._message_model = message_model
        self.db_manager = db_manager
        self.user_manager = user_manager
        self.message_service = message_service
        self.group_manager = group_manager
        self.message_manager = message_manager
        
        self._current_chat_user_id = None
        self._current_chat_group_id = None
        self._current_chat_type = 'user'

    def set_active_session(self, chat_type, user_id=None, group_id=None):
        self._current_chat_type = chat_type
        self._current_chat_user_id = user_id
        self._current_chat_group_id = group_id

    def process_received_message(self, message: Message):
        """处理私聊消息 (UI 安全线程)"""
        try:
            current_id = str(self._current_chat_user_id) if self._current_chat_user_id else ""
            sender_id = str(message.from_user_id)
            
            if sender_id == current_id:
                self.db_manager.mark_as_read(message.from_user_id, self.user_manager.current_user.user_id)
                message.is_read = True
                # 刷新模型，从数据库重新加载
                self._message_model.refresh()
                self.newMessageReceived.emit(message.to_dict())
            return True
        except Exception as e:
            logger.error(f"ChatController 处理私聊失败: {e}")
            return False

    def process_group_message(self, message: Message):
        """处理群聊消息 (UI 安全线程)"""
        try:
            if self._current_chat_type == 'group' and message.group_id == self._current_chat_group_id:
                # 刷新模型，从数据库重新加载
                self._message_model.refresh()
                self.groupMessageReceived.emit(message.to_dict())
            return True
        except Exception as e:
            logger.error(f"ChatController 处理群聊失败: {e}")
            return False

    def send_message(self, content):
        """发送消息统一入口"""
        if not content.strip(): return
        
        if self._current_chat_type == 'group' and self._current_chat_group_id:
            success = self.group_manager.send_group_message(
                group_id=self._current_chat_group_id,
                from_user_id=self.user_manager.current_user.user_id,
                from_username=self.user_manager.current_user.username,
                content=content
            )
            if success:
                # 刷新模型，从数据库重新加载最新消息
                self._message_model.refresh()
                msgs = self.db_manager.get_group_messages(self._current_chat_group_id, limit=1)
                if msgs:
                    self.newMessageSent.emit(msgs[-1].to_dict())
        
        elif self._current_chat_type == 'user' and self._current_chat_user_id:
            target_user = self.user_manager.get_user(self._current_chat_user_id)
            if not target_user or target_user.status != "online": return

            try:
                # 使用 message_manager 创建消息，确保包含 msg_id 和 timestamp
                msg = self.message_manager.create_message(
                    from_user_id=self.user_manager.current_user.user_id,
                    from_username=self.user_manager.current_user.username,
                    to_user_id=target_user.user_id,
                    to_username=target_user.username,
                    content=content
                )
                self.message_service.send_message(target_user.ip_address, target_user.tcp_port, msg.to_dict())
                self.db_manager.save_message(msg)
                # 刷新模型，从数据库重新加载
                self._message_model.refresh()
                self.newMessageSent.emit(msg.to_dict())
            except Exception as e:
                logger.error(f"发送私聊失败: {e}")
