"""
QML 后端桥接类 (Controller)
实现 MVC 架构中的控制层，通过子控制器分发业务
"""
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty
from src.core.models import Message
from src.core.user_manager import UserManager
from src.core.message_manager import MessageManager
from src.core.group_manager import GroupManager
from src.network.broadcast import BroadcastService
from src.network.message import MessageService
from src.database.db_manager import DatabaseManager
from src.ui.models import MessageListModel
from src.ui.controllers import UserController, ChatController, GroupController
from src.utils.logger import get_logger
import traceback

logger = get_logger(__name__)

class QmlBackend(QObject):
    """QML 与 Python 交互的调度中心"""

    # 声明所有供 QML 使用的信号 (保持接口兼容)
    userListChanged = pyqtSignal()
    chatHistoryChanged = pyqtSignal(list)
    newMessageReceived = pyqtSignal(dict)
    newMessageSent = pyqtSignal(dict)
    currentUserChanged = pyqtSignal()
    groupListChanged = pyqtSignal()
    groupMessageReceived = pyqtSignal(dict)
    
    # 内部跨线程信号 (保持私有以确保 UI 安全更新)
    _internalMessageSignal = pyqtSignal(object)
    _internalGroupMessageSignal = pyqtSignal(object)
    _internalGroupInviteSignal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        
        # 1. 初始化底层资源
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(db_manager=self.db_manager)
        self.message_manager = MessageManager()
        self.user_manager.initialize_current_user()
        
        # 2. 初始化 QML 模型（注入 db_manager）
        self._message_model = MessageListModel(db_manager=self.db_manager, parent=self)
        self._message_model.set_current_user_id(self.user_manager.current_user.user_id)

        # 3. 初始化网络底层服务
        self.broadcast_service = BroadcastService(
            on_user_discovered=self._on_user_discovered_raw,
            on_group_invite=self._on_group_invite_raw
        )
        self.message_service = MessageService(on_message_received=self._on_message_received_raw)
        self.group_manager = GroupManager(
            db_manager=self.db_manager,
            on_group_message_received=self._on_group_message_raw,
            on_broadcast_needed=self.broadcast_service.send_custom_broadcast
        )

        # 4. 初始化业务控制器 (拆分核心逻辑)
        self.user_ctrl = UserController(self.user_manager, self.db_manager)
        self.group_ctrl = GroupController(self.group_manager, self.user_manager)
        self.chat_ctrl = ChatController(
            self._message_model, self.db_manager, 
            self.user_manager, self.message_service, self.group_manager,
            self.message_manager
        )

        # 5. 绑定控制器信号到主信号 (供 QML 监听)
        self.user_ctrl.userListChanged.connect(self.userListChanged)
        self.user_ctrl.currentUserChanged.connect(self.currentUserChanged)
        self.group_ctrl.groupListChanged.connect(self.groupListChanged)
        self.chat_ctrl.newMessageReceived.connect(self.newMessageReceived)
        self.chat_ctrl.newMessageSent.connect(self.newMessageSent)
        self.chat_ctrl.groupMessageReceived.connect(self.groupMessageReceived)

        # 6. 绑定内部信号处理 (确保主线程执行业务)
        self._internalMessageSignal.connect(self.chat_ctrl.process_received_message)
        self._internalGroupMessageSignal.connect(self.chat_ctrl.process_group_message)
        self._internalGroupInviteSignal.connect(self.group_ctrl.process_group_invite)

        # 7. 启动常驻服务
        self._start_services()

    def _start_services(self):
        try:
            self.broadcast_service.set_current_user(self.user_manager.current_user)
            self.broadcast_service.start()
            self.message_service.start()
            self.group_manager.start()
            logger.info("系统各模块子服务已启动")
        except Exception as e:
            logger.error(f"子服务启动失败: {e}\n{traceback.format_exc()}")

    # --- 属性接口 (映射到控制器) ---
    
    @pyqtProperty(QObject, constant=True)
    def messageModel(self): return self._message_model

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserId(self): return self.user_manager.current_user.user_id

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserName(self): return self.user_manager.current_user.username

    @pyqtProperty(str, notify=currentUserChanged)
    def currentUserIp(self): return self.user_manager.current_user.ip_address

    @pyqtProperty(list, notify=userListChanged)
    def onlineUsers(self): return self.user_ctrl.get_online_users_data()

    @pyqtProperty(str, notify=userListChanged)
    def currentChatUserStatus(self):
        user = self.user_manager.get_user(self.chat_ctrl._current_chat_user_id)
        return user.status if user else "offline"

    @pyqtProperty(list, notify=groupListChanged)
    def groupList(self): return self.group_ctrl.get_group_list_data()

    # --- 槽函数接口 (转发到控制器) ---

    @pyqtSlot(str)
    def selectUser(self, user_id):
        """选择私聊用户"""
        self.chat_ctrl.set_active_session('user', user_id=user_id)
        self.user_ctrl.set_current_chat_user_id(user_id)
        self.group_ctrl.set_current_chat_group_id(None)
        
        # 标记消息已读并刷新模型
        self.db_manager.mark_as_read(user_id, self.user_manager.current_user.user_id)
        self._message_model.set_active_session('user', user_id=user_id)
        self.userListChanged.emit()

    @pyqtSlot(str)
    def selectGroup(self, group_id):
        """选择群聊"""
        self.chat_ctrl.set_active_session('group', group_id=group_id)
        self.group_ctrl.set_current_chat_group_id(group_id)
        self.user_ctrl.set_current_chat_user_id(None)
        
        # 刷新模型以显示群聊消息
        self._message_model.set_active_session('group', group_id=group_id)
        self.groupListChanged.emit()

    @pyqtSlot(str, list)
    def createGroup(self, group_name, member_user_ids):
        if self.group_ctrl.create_group(group_name, member_user_ids):
            logger.info(f"群组 '{group_name}' 创建指令分发成功")

    @pyqtSlot(str)
    def sendMessage(self, content):
        self.chat_ctrl.send_message(content)

    @pyqtSlot()
    def stop(self):
        """统一停止所有服务"""
        try:
            self.broadcast_service.send_offline()
            self.broadcast_service.stop()
            self.message_service.stop()
            self.group_manager.stop()
            self.db_manager.destroy()
        except Exception as e:
            logger.error(f"系统关闭清理失败: {e}")

    # --- 底层服务回调 (转发到内部安全信号) ---

    def _on_message_received_raw(self, message_data: dict):
        """接收私聊消息（网络线程回调）"""
        message = Message.from_dict(message_data)
        # 先保存到数据库
        self.db_manager.save_message(message)
        # 触发用户列表刷新（更新未读计数）
        self.userListChanged.emit()
        # 再触发UI更新信号
        self._internalMessageSignal.emit(message)

    def _on_group_message_raw(self, message: Message):
        if message.from_user_id != self.user_manager.current_user.user_id:
            self._internalGroupMessageSignal.emit(message)

    def _on_user_discovered_raw(self, user_data: dict, addr: tuple):
        self.user_ctrl.handle_user_discovered(user_data)

    def _on_group_invite_raw(self, invite_data: dict):
        self._internalGroupInviteSignal.emit(invite_data)
