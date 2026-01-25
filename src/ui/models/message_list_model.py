"""消息列表数据模型
用于 QML ListView 高效渲染消息列表
"""
from PyQt5.QtCore import QAbstractListModel, Qt, QVariant


class MessageListModel(QAbstractListModel):
    """消息列表模型，用于 QML 高效渲染"""
    
    # 定义 Roles（数据角色）
    ContentRole = Qt.UserRole + 1
    FromUserIdRole = Qt.UserRole + 2
    FromUsernameRole = Qt.UserRole + 3
    TimestampRole = Qt.UserRole + 4
    IsMineRole = Qt.UserRole + 5
    TypeRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._messages = []
        self._current_user_id = ""

    def set_current_user_id(self, user_id):
        """设置当前用户 ID，用于判断消息是否为我的"""
        self._current_user_id = user_id
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """返回消息数量"""
        return len(self._messages)

    def data(self, index, role):
        """根据索引和角色返回数据"""
        if not index.isValid() or index.row() >= len(self._messages):
            return QVariant()
        
        msg = self._messages[index.row()]
        
        if role == self.ContentRole:
            return msg.get('content', '')
        elif role == self.FromUserIdRole:
            return msg.get('from_user_id', '')
        elif role == self.FromUsernameRole:
            return msg.get('from_username', '')
        elif role == self.TimestampRole:
            return msg.get('timestamp', 0)
        elif role == self.IsMineRole:
            return str(msg.get('from_user_id')) == str(self._current_user_id)
        elif role == self.TypeRole:
            return msg.get('type', 'TEXT')
            
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

    def set_messages(self, messages):
        """全量更新消息"""
        self.beginResetModel()
        self._messages = messages
        self.endResetModel()

    def add_message(self, message_dict):
        """增量添加消息"""
        row = len(self._messages)
        print(f"[DEBUG] add_message 被调用！当前消息数: {row}")
        print(f"[DEBUG] 消息内容: {message_dict}")
        print(f"[DEBUG] Model parent: {self.parent()}")
        
        # 使用 beginInsertRows/endInsertRows
        from PyQt5.QtCore import QModelIndex
        print(f"[DEBUG] 准备调用 beginInsertRows({row}, {row})")
        self.beginInsertRows(QModelIndex(), row, row)
        print(f"[DEBUG] beginInsertRows 调用完成")
        self._messages.append(message_dict)
        print(f"[DEBUG] 消息已添加到内部列表")
        self.endInsertRows()
        print(f"[DEBUG] endInsertRows 调用完成")
        
        print(f"[DEBUG] 消息添加完成，新的消息数: {len(self._messages)}")
        print(f"[DEBUG] rowCount() 返回: {self.rowCount()}")
