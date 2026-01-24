"""
QML 后端桥接类 (Controller)
实现 MVC 架构中的控制层
"""
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant
from src.core.models import User, Message
from src.core.user_manager import UserManager
from src.core.message_manager import MessageManager
from src.network.broadcast import BroadcastService
from src.network.message import MessageService
from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger
import traceback

logger = get_logger(__name__)


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

        # 初始化当前用户
        self.user_manager.initialize_current_user()

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

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserName(self):
        return self.user_manager.current_user.username

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserIp(self):
        return self.user_manager.current_user.ip_address

    @pyqtProperty(list, notify=userListChanged)
    def onlineUsers(self):
        """返回在线用户列表供 QML 渲染"""
        users = []
        for user in self.user_manager.get_online_users():
            users.append({
                'user_id': user.user_id,
                'username': user.username,
                'ip': user.ip_address,
                'is_current': user.user_id == self._current_chat_user_id
            })
        return users

    # --- 槽函数供 QML 调用 ---

    @pyqtSlot(str)
    def selectUser(self, user_id):
        """用户点击列表，选择聊天对象"""
        self._current_chat_user_id = user_id
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
            history_list = [msg.to_dict() for msg in history]
            self.chatHistoryChanged.emit(history_list)
            self.userListChanged.emit()  # 更新选中状态

    @pyqtSlot(str)
    def sendMessage(self, content):
        """从 QML 发送消息"""
        if not self._current_chat_user_id or not content.strip():
            return

        target_user = self.user_manager.get_user(self._current_chat_user_id)
        if not target_user:
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
            logger.info(f"已发送消息: {target_user.ip_address},{target_user.tcp_port},{message.content}")
            # 保存并反馈给 UI
            self.db_manager.save_message(message)
            self.newMessageSent.emit(message.to_dict())

        except Exception as e:
            logger.error(f"发送消息失败:{traceback.format_exc()}")

    # --- 内部回调 ---

    def _on_user_discovered(self, user_data: dict, addr: tuple):
        """用户发现回调"""
        user = User(
            user_id=user_data.get('user_id', ''),
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
            message = Message.from_dict(message_data)
            self.db_manager.save_message(message)

            # 如果是当前正在聊天的用户发来的消息，立即推送到界面
            if message.from_user_id == self._current_chat_user_id:
                self.newMessageReceived.emit(message.to_dict())
            else:
                # 提示有新消息（此处可扩展通知逻辑）
                pass
        except Exception as e:
            logger.error(f"处理接收消息失败: {e}")

    @pyqtSlot()
    def stop(self):
        """停止所有服务"""
        self.broadcast_service.stop()
        self.message_service.stop()
