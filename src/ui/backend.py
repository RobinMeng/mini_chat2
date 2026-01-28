"""
QML 后端桥接类 (Controller)
实现 MVC 架构中的控制层
"""
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QTimer
from src.core.models import User, Message, Group
from src.core.user_manager import UserManager
from src.core.message_manager import MessageManager
from src.core.group_manager import GroupManager
from src.network.broadcast import BroadcastService
from src.network.message import MessageService
from src.database.db_manager import DatabaseManager
from src.ui.models import MessageListModel
from src.utils.logger import get_logger
import traceback
import time

logger = get_logger(__name__)


class QmlBackend(QObject):
    """QML 与 Python 交互的中转类"""

    # 信号定义
    userListChanged = pyqtSignal()
    chatHistoryChanged = pyqtSignal(list)
    newMessageReceived = pyqtSignal(dict)
    newMessageSent = pyqtSignal(dict)
    currentUserChanged = pyqtSignal()
    groupListChanged = pyqtSignal()  # 群组列表变化
    groupMessageReceived = pyqtSignal(dict)  # 群组消息接收
    
    # 内部跨线程专用信号
    _internalMessageSignal = pyqtSignal(object)
    _internalGroupMessageSignal = pyqtSignal(object)  # 群组消息内部信号

    def __init__(self):
        super().__init__()
        
        # 绑定内部信号到处理函数 (确保在主线程执行)
        self._internalMessageSignal.connect(self._ui_safe_process_received_message)
        self._internalGroupMessageSignal.connect(self._ui_safe_process_group_message)

        # 初始化管理器 (Model 层)
        self.user_manager = UserManager()
        self.message_manager = MessageManager()
        self.db_manager = DatabaseManager()

        # 初始化消息列表模型（设置 parent 以确保信号正确传递）
        self._message_model = MessageListModel(self)

        # 初始化当前用户
        self.user_manager.initialize_current_user()
        self._message_model.set_current_user_id(self.user_manager.current_user.user_id)

        # 网络服务
        self.broadcast_service = BroadcastService(on_user_discovered=self._on_user_discovered)
        self.message_service = MessageService(on_message_received=self._on_message_received)
        
        # 群组管理器
        self.group_manager = GroupManager(
            db_manager=self.db_manager,
            on_group_message_received=self._on_group_message_received
        )

        # 当前聊天对象 ID
        self._current_chat_user_id = None
        
        # 当前选中的群组 ID
        self._current_chat_group_id = None
        
        # 当前聊天类型：'user' 或 'group'
        self._current_chat_type = 'user'

        # 启动服务
        self._start_services()

    def _start_services(self):
        """启动网络服务"""
        try:
            self.broadcast_service.set_current_user(self.user_manager.current_user)
            self.broadcast_service.start()
            self.message_service.start()
            self.group_manager.start()
            logger.info("QML 后端网络服务已启动")
        except Exception as e:
            logger.error(f"启动网络服务失败: {e}\n{traceback.format_exc()}")

    # --- 属性供 QML 读取 ---
    @pyqtProperty(QObject, constant=True)
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
        """返回用户列表供 QML 渲染"""
        users = []
        current_me_id = self.user_manager.current_user.user_id
        all_users = sorted(self.user_manager.get_all_users(),
                           key=lambda u: u.status != "online")

        for user in all_users:
            unread = self.db_manager.get_unread_count(user.user_id, current_me_id)
            users.append({
                'user_id': user.user_id,
                'username': user.username,
                'ip': user.ip_address,
                'is_current': user.user_id == self._current_chat_user_id,
                'unread_count': unread,
                'status': user.status
            })
        return users

    @pyqtProperty(str, notify=userListChanged)
    def currentChatUserStatus(self):
        """当前聊天对象的在线状态"""
        if not self._current_chat_user_id:
            return "offline"
        user = self.user_manager.get_user(self._current_chat_user_id)
        return user.status if user else "offline"

    @pyqtProperty(list, notify=groupListChanged)
    def groupList(self):
        """返回群组列表供 QML 渲染"""
        groups = []
        for group in self.group_manager.get_all_groups():
            groups.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'member_count': len(group.member_ids),
                'is_current': group.group_id == self._current_chat_group_id
            })
        return groups

    # --- 槽函数供 QML 调用 ---

    @pyqtSlot(str)
    def selectUser(self, user_id):
        """用户点击列表，选择聊天对象"""
        self._current_chat_type = 'user'
        self._current_chat_user_id = user_id
        self._current_chat_group_id = None
        self.db_manager.mark_as_read(user_id, self.user_manager.current_user.user_id)
        
        user = self.user_manager.get_user(user_id)
        if user:
            history = self.db_manager.get_messages(
                self.user_manager.current_user.user_id,
                user_id,
                limit=50
            )
            history_list = [msg.to_dict() for msg in history]
            self._message_model.set_messages(history_list)
            self.userListChanged.emit()

    @pyqtSlot(str)
    def selectGroup(self, group_id):
        """选择群组聊天"""
        self._current_chat_type = 'group'
        self._current_chat_group_id = group_id
        self._current_chat_user_id = None
        
        group = self.group_manager.get_group(group_id)
        if group:
            history = self.db_manager.get_group_messages(group_id, limit=50)
            history_list = [msg.to_dict() for msg in history]
            self._message_model.set_messages(history_list)
            self.groupListChanged.emit()

    @pyqtSlot(str, list)
    def createGroup(self, group_name, member_user_ids):
        """创建群组"""
        try:
            group = self.group_manager.create_group(
                group_name=group_name,
                owner_id=self.user_manager.current_user.user_id,
                member_ids=member_user_ids
            )
            if group:
                self.groupListChanged.emit()
                logger.info(f"群组创建成功: {group_name}")
        except Exception as e:
            logger.error(f"创建群组失败: {e}")

    @pyqtSlot(str)
    def sendMessage(self, content):
        """从 QML 发送消息"""
        if not content.strip():
            return
        
        # 判断当前是群聊还是私聊
        if self._current_chat_type == 'group' and self._current_chat_group_id:
            # 发送群组消息
            success = self.group_manager.send_group_message(
                group_id=self._current_chat_group_id,
                from_user_id=self.user_manager.current_user.user_id,
                from_username=self.user_manager.current_user.username,
                content=content
            )
            if success:
                # 获取刚发送的消息
                messages = self.db_manager.get_group_messages(self._current_chat_group_id, limit=1)
                if messages:
                    self._message_model.add_message(messages[-1].to_dict())
                    self.newMessageSent.emit(messages[-1].to_dict())
        
        elif self._current_chat_type == 'user' and self._current_chat_user_id:
            # 发送私人消息
            target_user = self.user_manager.get_user(self._current_chat_user_id)
            if not target_user or target_user.status != "online":
                return

            try:
                message = self.message_manager.create_message(
                    from_user_id=self.user_manager.current_user.user_id,
                    from_username=self.user_manager.current_user.username,
                    to_user_id=target_user.user_id,
                    to_username=target_user.username,
                    content=content
                )
                self.message_service.send_message(target_user.ip_address, target_user.tcp_port, message.to_dict())
                self.db_manager.save_message(message)
                
                # 发送消息始终在主线程，直接操作
                self._message_model.add_message(message.to_dict())
                self.newMessageSent.emit(message.to_dict())
            except Exception as e:
                logger.error(f"发送消息失败: {e}")

    # --- 内部逻辑处理 ---

    def _on_message_received(self, message_data: dict):
        """TCP 消息接收回调 (后台线程运行)"""
        try:
            message = Message.from_dict(message_data)
            
            # 1. 数据库保存 (留在后台线程)
            self.db_manager.save_message(message)
            
            # 2. 通过信号通知主线程 (安全跨线程)
            self._internalMessageSignal.emit(message)
            
        except Exception as e:
            logger.error(f"处理接收消息失败: {e}")

    def _ui_safe_process_received_message(self, message):
        """(主线程运行) 响应 _internalMessageSignal"""
        try:
            # 严格的 ID 匹配
            current_id = str(self._current_chat_user_id) if self._current_chat_user_id else ""
            sender_id = str(message.from_user_id)
            
            if sender_id == current_id:
                # 标记已读 (数据库更新)
                self.db_manager.mark_as_read(message.from_user_id, self.user_manager.current_user.user_id)
                message.is_read = True
                # 更新 ListView
                self._message_model.add_message(message.to_dict())
                # 触发 QML 滚动
                self.newMessageReceived.emit(message.to_dict())
            
            self.userListChanged.emit()
        except Exception as e:
            logger.error(f"UI 处理失败: {e}")

    def _on_group_message_received(self, message: Message):
        """群组消息接收回调 (后台线程运行)"""
        try:
            # 通过信号通知主线程
            self._internalGroupMessageSignal.emit(message)
        except Exception as e:
            logger.error(f"处理群组消息失败: {e}")

    def _ui_safe_process_group_message(self, message: Message):
        """(主线程运行) 处理群组消息"""
        try:
            # 如果当前正在聊该群组
            if self._current_chat_type == 'group' and message.group_id == self._current_chat_group_id:
                self._message_model.add_message(message.to_dict())
                self.groupMessageReceived.emit(message.to_dict())
            
            # 更新群组列表（显示未读数）
            self.groupListChanged.emit()
        except Exception as e:
            logger.error(f"UI 处理群组消息失败: {e}")

    def _on_user_discovered(self, user_data: dict, addr: tuple):
        """用户发现回调"""
        user_id = user_data.get('user_id', '')
        if user_data.get('type') == 'BYE':
            if self.user_manager.set_user_offline(user_id):
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

    @pyqtSlot()
    def stop(self):
        """停止所有服务"""
        try:
            self.broadcast_service.send_offline()
            self.broadcast_service.stop()
            self.message_service.stop()
            self.group_manager.stop()
            self.db_manager.destroy()
        except Exception as e:
            logger.error(f"退出清理失败: {e}")
