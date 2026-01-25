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
from src.ui.models import MessageListModel
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
            
        # 初始化消息列表模型（设置 parent 以确保信号正确传递）
        self._message_model = MessageListModel(self)
            
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
        logger.info(f"👆 用户点击选择聊天对象: {user_id}")
        self._current_chat_user_id = user_id
        logger.info(f"📌 当前聊天对象已更新为: {self._current_chat_user_id}")
        
        # 标记来自该用户的所有消息为已读
        self.db_manager.mark_as_read(user_id, self.user_manager.current_user.user_id)
        
        user = self.user_manager.get_user(user_id)
        if user:
            logger.info(f"切换聊天对象到: {user.username}")
            # 加载历史消息
            logger.info(f"[DEBUG] 当前用户ID: {self.user_manager.current_user.user_id}")
            logger.info(f"[DEBUG] 目标用户ID: {user_id}")
            history = self.db_manager.get_messages(
                self.user_manager.current_user.user_id,
                user_id,
                limit=50
            )
            logger.info(f"[DEBUG] 查询返回的 history 类型: {type(history)}, 长度: {len(history)}")
            # 转换为字典列表
            history_list = []
            for msg in history:
                msg_dict = msg.to_dict()
                logger.info(f"[DEBUG] 消息: {msg_dict.get('msg_id')} - {msg_dict.get('content')[:20]}...")
                history_list.append(msg_dict)
            
            logger.info(f"加载了 {len(history_list)} 条历史消息")
            logger.info(f"[DEBUG] 准备调用 set_messages")
            self._message_model.set_messages(history_list)
            logger.info(f"[DEBUG] set_messages 调用完成")
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
            
            # 诊断日志
            logger.info(f"[接收消息] 发送者: {message.from_user_id}")
            logger.info(f"[接收消息] 当前聊天对象: {self._current_chat_user_id}")
            logger.info(f"[接收消息] ID类型: 发送者={type(message.from_user_id).__name__}, 当前={type(self._current_chat_user_id).__name__ if self._current_chat_user_id else 'None'}")
            logger.info(f"[接收消息] 是否匹配: {message.from_user_id == self._current_chat_user_id}")
            
            # 先保存到数据库（默认 is_read=False）
            # 注意：如果消息已存在，忽略错误
            save_result = self.db_manager.save_message(message)
            if not save_result:
                logger.warning(f"消息已存在或保存失败: {message.msg_id}，但仍继续处理")
            
            # 如果是当前正在聊天的用户发来的消息
            if message.from_user_id == self._current_chat_user_id:
                logger.info(f"✅ 匹配当前聊天对象，立即显示消息")
                # 立即标记为已读
                self.db_manager.mark_as_read(message.from_user_id, self.user_manager.current_user.user_id)
                # 添加到界面
                message.is_read = True  # 同步 UI 层的状态
                logger.info(f"[Backend] 准备调用 add_message，当前 Model 消息数: {len(self._message_model._messages)}")
                self._message_model.add_message(message.to_dict())
                logger.info(f"[Backend] add_message 调用完成，新的 Model 消息数: {len(self._message_model._messages)}")
                # 触发滚动信号
                self.newMessageReceived.emit(message.to_dict())
            else:
                logger.info(f"❌ 不是当前聊天对象，不自动显示")
            
            # 更新用户列表（刷新未读数）
            self.userListChanged.emit()
            
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
