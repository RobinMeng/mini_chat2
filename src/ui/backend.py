"""
QML 后端桥接类 (Controller)
实现 MVC 架构中的控制层
"""
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QAbstractListModel, Qt
from src.core.models import User, Message
from src.core.user_manager import UserManager
from src.core.message_manager import MessageManager
from src.network.broadcast import BroadcastService
from src.network.message import MessageService
from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger
import traceback

logger = get_logger(__name__)

class MessageListModel(QAbstractListModel):
    """消息列表模型，用于 QML 高效渲染"""
    
    # 定义 Roles
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
        self._current_user_id = user_id
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self._messages)

    def data(self, index, role):
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
        self.beginInsertRows(self.index(len(self._messages)), len(self._messages), len(self._messages))
        self._messages.append(message_dict)
        self.endInsertRows()

class QmlBackend(QObject):
    """QML 与 Python 交互的中转类"""

    # 信号定义
    userListChanged = pyqtSignal()
    chatHistoryChanged = pyqtSignal(list)
    newMessageReceived = pyqtSignal(dict)
    newMessageSent = pyqtSignal(dict)
    currentUserChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
            
        # 初始化管理器 (Model 层)
        self.user_manager = UserManager()
        self.message_manager = MessageManager()
        self.db_manager = DatabaseManager()
            
        # 初始化消息列表模型
        self._message_model = MessageListModel()
            
        # 初始化当前用户
        self.user_manager.initialize_current_user()
        self._message_model.set_current_user_id(self.user_manager.current_user.user_id)
    
        # 网络服务
        self.broadcast_service = BroadcastService(on_user_discovered=self._on_user_discovered)
        self.message_service = MessageService(on_message_received=self._on_message_received)

        # 当前聊天对象 ID
        self._current_chat_user_id = None

        # 启动服务
        self._start_services()

    def _start_services(self):
        """启动网络服务"""
        try:
            self.broadcast_service.set_current_user(self.user_manager.current_user)
            self.broadcast_service.start()
            self.message_service.start()
            logger.info("QML 后端网络服务已启动")
        except Exception as e:
            # 详细报错信息
            logger.error(f"启动网络服务失败: {e}\n{traceback.format_exc()}")

    # --- 属性供 QML 读取 ---
    @pyqtProperty(QObject, notify=currentUserChanged)
    def messageModel(self):
        return self._message_model

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserId(self):
        return self.user_manager.current_user.user_id

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserName(self):
        return self.user_manager.current_user.username

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserIp(self):
        return self.user_manager.current_user.ip_address

    @pyqtProperty(list, notify=userListChanged)
    def onlineUsers(self):
        """返回用户列表供 QML 渲染 (包含在线和刚下线的)"""
        users = []
        current_me_id = self.user_manager.current_user.user_id
        # 获取所有已知用户，按在线状态排序（在线在前）
        all_users = sorted(self.user_manager.get_all_users(), 
                          key=lambda u: u.status != "online")
        
        for user in all_users:
            # 获取来自该用户的未读消息数
            unread = self.db_manager.get_unread_count(user.user_id, current_me_id)
            users.append({
                'user_id': user.user_id,
                'username': user.username,
                'ip': user.ip_address,
                'is_current': user.user_id == self._current_chat_user_id,
                'unread_count': unread,
                'status': user.status # "online" 或 "offline"
            })
        return users

    @pyqtProperty(str, notify=userListChanged)
    def currentChatUserStatus(self):
        """当前聊天对象的在线状态"""
        if not self._current_chat_user_id:
            return "offline"
        user = self.user_manager.get_user(self._current_chat_user_id)
        return user.status if user else "offline"

    # --- 槽函数供 QML 调用 ---

    @pyqtSlot(str)
    def selectUser(self, user_id):
        """用户点击列表，选择聊天对象"""
        self._current_chat_user_id = user_id
        
        # 标记来自该用户的所有消息为已读
        self.db_manager.mark_as_read(user_id, self.user_manager.current_user.user_id)
        
        user = self.user_manager.get_user(user_id)
        if user:
            logger.info(f"切换聊天对象到: {user.username}")
            # 加载历史消息
            history = self.db_manager.get_messages(
                self.user_manager.current_user.user_id,
                user_id,
                limit=50
            )
            # 转换为字典列表
            history_list = []
            for msg in history:
                history_list.append(msg.to_dict())
                            
            self._message_model.set_messages(history_list)
            self.userListChanged.emit() # 更新选中状态
            
    @pyqtSlot(str)
    def sendMessage(self, content):
        """从 QML 发送消息"""
        if not self._current_chat_user_id or not content.strip():
            return

        target_user = self.user_manager.get_user(self._current_chat_user_id)
        if not target_user:
            return
            
        if target_user.status != "online":
            logger.warning(f"无法向离线用户发送消息: {target_user.username}")
            return

        try:
            # 创建并发送
            message = self.message_manager.create_message(
                from_user_id=self.user_manager.current_user.user_id,
                from_username=self.user_manager.current_user.username,
                to_user_id=target_user.user_id,
                to_username=target_user.username,
                content=content
            )

            self.message_service.send_message(
                target_user.ip_address,
                target_user.tcp_port,
                message.to_dict()
            )
            logger.info(f"已发送消息: {target_user.ip_address},{target_user.tcp_port},{message.to_dict()}")
            # 保存并反馈给 UI
            self.db_manager.save_message(message)
            self._message_model.add_message(message.to_dict())
            self.newMessageSent.emit(message.to_dict())

        except Exception as e:
            logger.error(f"发送消息失败:{traceback.format_exc()}")

    # --- 内部回调 ---

    def _on_user_discovered(self, user_data: dict, addr: tuple):
        """用户发现回调"""
        msg_type = user_data.get('type', 'HEARTBEAT')
        user_id = user_data.get('user_id', '')
        
        if msg_type == 'BYE':
            if self.user_manager.set_user_offline(user_id):
                logger.info(f"收到下线广播，用户状态设为下线: {user_id}")
                self.userListChanged.emit()
            return

        user = User(
            user_id=user_id,
            username=user_data.get('username', ''),
            hostname=user_data.get('hostname', ''),
            ip_address=user_data.get('ip', ''),
            tcp_port=user_data.get('tcp_port', 10000)
        )
        if self.user_manager.add_user(user):
            self.userListChanged.emit()

    def _on_message_received(self, message_data: dict):
        """TCP 消息接收回调"""
        try:
            logger.debug(f"收到原始消息数据: {message_data}")
            message = Message.from_dict(message_data)
            
            # 如果是当前正在聊天的用户发来的消息，立即标记为已读并推送到界面
            if message.from_user_id == self._current_chat_user_id:
                message.is_read = True
                self._message_model.add_message(message.to_dict())
                self.newMessageReceived.emit(message.to_dict())
            
            self.db_manager.save_message(message)
            self.userListChanged.emit() # 无论是否当前聊天，都触发列表刷新以更新未读数
            
        except Exception as e:
            logger.error(f"处理接收消息失败: {e}")

    @pyqtSlot()
    def stop(self):
        """停止所有服务并清理数据 (阅后即焚)"""
        try:
            self.broadcast_service.send_offline() # 主动通知其他用户下线
            self.broadcast_service.stop()
            self.message_service.stop()
            self.db_manager.destroy() # 退出即物理删除数据库文件
            logger.info("应用服务已停止，下线广播已发送，本地数据已清理")
        except Exception as e:
            logger.error(f"退出清理失败: {e}")
