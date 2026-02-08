"""消息列表数据模型（基于数据库查询）
用于 QML ListView 高效渲染消息列表
"""
from PyQt5.QtCore import QAbstractListModel, Qt, QVariant
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MessageListModel(QAbstractListModel):
    """消息列表模型，直接从数据库查询数据"""
    
    # 定义 Roles（数据角色）
    ContentRole = Qt.UserRole + 1
    FromUserIdRole = Qt.UserRole + 2
    FromUsernameRole = Qt.UserRole + 3
    TimestampRole = Qt.UserRole + 4
    IsMineRole = Qt.UserRole + 5
    TypeRole = Qt.UserRole + 6

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._current_user_id = ""
        self._current_chat_user_id = None  # 当前聊天对象 ID（私聊）
        self._current_chat_group_id = None  # 当前群聊 ID
        self._chat_type = 'user'  # 'user' 或 'group'

    def set_current_user_id(self, user_id):
        """设置当前用户 ID，用于判断消息是否为我的"""
        self._current_user_id = user_id

    def set_active_session(self, chat_type, user_id=None, group_id=None):
        """设置当前活跃会话（私聊或群聊）"""
        self._chat_type = chat_type
        self._current_chat_user_id = user_id
        self._current_chat_group_id = group_id
        self.refresh()

    def refresh(self):
        """刷新数据（从数据库重新加载）"""
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=None):
        """返回消息数量（从数据库查询）"""
        if not self.db_manager:
            return 0
        
        try:
            if self._chat_type == 'group' and self._current_chat_group_id:
                messages = self.db_manager.get_group_messages(self._current_chat_group_id)
                return len(messages)
            elif self._chat_type == 'user' and self._current_chat_user_id:
                messages = self.db_manager.get_messages(
                    self._current_user_id, 
                    self._current_chat_user_id
                )
                return len(messages)
            return 0
        except Exception as e:
            logger.error(f"查询消息数量失败: {e}")
            return 0

    def data(self, index, role):
        """根据索引和角色返回数据（从数据库查询）"""
        if not index.isValid() or not self.db_manager:
            return QVariant()
        
        try:
            # 从数据库获取消息列表
            if self._chat_type == 'group' and self._current_chat_group_id:
                messages = self.db_manager.get_group_messages(self._current_chat_group_id)
            elif self._chat_type == 'user' and self._current_chat_user_id:
                messages = self.db_manager.get_messages(
                    self._current_user_id,
                    self._current_chat_user_id
                )
            else:
                return QVariant()
            
            # 检查索引范围
            if index.row() >= len(messages):
                return QVariant()
            
            msg = messages[index.row()]
            
            # 根据 role 返回对应数据
            if role == self.ContentRole:
                return msg.content
            elif role == self.FromUserIdRole:
                return msg.from_user_id
            elif role == self.FromUsernameRole:
                return msg.from_username
            elif role == self.TimestampRole:
                return msg.timestamp
            elif role == self.IsMineRole:
                return str(msg.from_user_id) == str(self._current_user_id)
            elif role == self.TypeRole:
                return msg.type
                
        except Exception as e:
            logger.error(f"获取消息数据失败: {e}")
            return QVariant()
            
        return QVariant()

    def roleNames(self):
        """映射 Role 名到 QML 变量名"""
        return {
            self.ContentRole: b"content",
            self.FromUserIdRole: b"from_user_id",
            self.FromUsernameRole: b"from_username",
            self.TimestampRole: b"timestamp",
            self.IsMineRole: b"is_mine",
            self.TypeRole: b"msg_type"
        }
