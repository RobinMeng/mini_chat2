"""
主窗口 - 业务逻辑层
使用 .ui 文件生成的界面
"""
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

from src.ui.generated.ui_main_window import Ui_MainWindow
from src.core.models import User, Message
from src.core.user_manager import UserManager
from src.core.message_manager import MessageManager
from src.network.broadcast import BroadcastService
from src.network.message import MessageService
from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """主窗口类 - 继承自生成的 UI 类"""
    
    # 信号定义  dict, tuple 用户数据和地址
    user_discovered_signal = pyqtSignal(dict, tuple)
    message_received_signal = pyqtSignal(dict, tuple)
    
    def __init__(self):
        super().__init__()
        
        # 加载 UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 初始化管理器
        ## 用户管理
        self.user_manager = UserManager()
        ## 消息管理
        self.message_manager = MessageManager()
        ## 数据库管理
        self.db_manager = DatabaseManager()
        
        # 初始化当前用户
        self.user_manager.initialize_current_user()
        
        # 网络服务
        self.broadcast_service = BroadcastService(on_user_discovered=self._on_user_discovered)
        self.message_service = MessageService(on_message_received=self._on_message_received)
        
        # 当前聊天对象
        self.current_chat_user = None
        
        # 连接信号槽
        self._connect_signals()
        
        # 启动服务
        self._start_services()
    
    def _connect_signals(self):
        """连接信号槽"""
        # UI 控件信号
        self.ui.userList.itemDoubleClicked.connect(self._on_user_double_clicked)
        self.ui.sendBtn.clicked.connect(self._send_message)
        self.ui.sendFileBtn.clicked.connect(self._send_file)
        self.ui.messageInput.installEventFilter(self)
        
        # 网络信号
        self.user_discovered_signal.connect(self._handle_user_discovered)
        self.message_received_signal.connect(self._handle_message_received)
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理快捷键"""
        if obj == self.ui.messageInput and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self._send_message()
                return True
        return super().eventFilter(obj, event)
    
    def _start_services(self):
        """启动网络服务"""
        try:
            # 设置当前用户
            self.broadcast_service.set_current_user(self.user_manager.current_user)
            
            # 启动服务
            self.broadcast_service.start()
            self.message_service.start()
            
            logger.info("网络服务已启动")
            self.statusBar().showMessage(
                f"已上线: {self.user_manager.current_user.username} "
                f"({self.user_manager.current_user.ip_address})"
            )
        except Exception as e:
            logger.error(f"启动网络服务失败: {e}")
            QMessageBox.critical(self, "错误", f"启动网络服务失败: {e}")
    
    def _on_user_discovered(self, user_data: dict, addr: tuple):
        """用户发现回调"""
        self.user_discovered_signal.emit(user_data, addr)
    
    @pyqtSlot(dict, tuple)
    def _handle_user_discovered(self, user_data: dict, addr: tuple):
        """处理发现的用户"""
        try:
            user = User(
                user_id=user_data.get('user_id', ''),
                username=user_data.get('username', ''),
                hostname=user_data.get('hostname', ''),
                ip_address=user_data.get('ip', ''),
                tcp_port=user_data.get('tcp_port', 10000)
            )
            
            # 添加到用户管理器
            if self.user_manager.add_user(user):
                self._refresh_user_list()
        except Exception as e:
            logger.error(f"处理用户发现失败: {e}")
    
    def _refresh_user_list(self):
        """刷新用户列表"""
        self.ui.userList.clear()
        for user in self.user_manager.get_online_users():
            item = QListWidgetItem(f"{user.username} ({user.ip_address})")
            item.setData(Qt.UserRole, user.user_id)
            self.ui.userList.addItem(item)
    
    def _on_user_double_clicked(self, item: QListWidgetItem):
        """用户列表双击事件"""
        user_id = item.data(Qt.UserRole)
        user = self.user_manager.get_user(user_id)
        
        if user:
            self.current_chat_user = user
            self.ui.chatTitle.setText(f"与 {user.username} 聊天")
            self.ui.sendBtn.setEnabled(True)
            self.ui.sendFileBtn.setEnabled(True)
            
            # 加载历史消息
            self._load_chat_history(user_id)
            
            logger.info(f"开始与 {user.username} 聊天")
    
    def _load_chat_history(self, user_id: str):
        """加载聊天历史"""
        self.ui.messageDisplay.clear()
        
        # 从数据库加载历史消息
        messages = self.db_manager.get_messages(
            self.user_manager.current_user.user_id,
            user_id,
            limit=50
        )
        
        for msg in messages:
            self._display_message(msg)
    
    def _send_message(self):
        """发送消息"""
        if not self.current_chat_user:
            return
        
        content = self.ui.messageInput.toPlainText().strip()
        if not content:
            return
        
        try:
            # 创建消息
            message = self.message_manager.create_message(
                from_user=self.user_manager.current_user,
                to_user=self.current_chat_user,
                content=content
            )
            
            # 发送消息
            self.message_service.send_message(
                self.current_chat_user.ip_address,
                self.current_chat_user.tcp_port,
                message.to_dict()
            )
            
            # 保存到数据库
            self.db_manager.save_message(message)
            
            # 显示消息
            self._display_message(message, is_mine=True)
            
            # 清空输入框
            self.ui.messageInput.clear()
            
            logger.info(f"消息已发送到 {self.current_chat_user.username}")
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            QMessageBox.warning(self, "发送失败", f"发送消息失败: {e}")
    
    def _send_file(self):
        """发送文件"""
        QMessageBox.information(self, "提示", "文件传输功能开发中...")
    
    def _on_message_received(self, message_data: dict, addr: tuple):
        """消息接收回调"""
        self.message_received_signal.emit(message_data, addr)
    
    @pyqtSlot(dict, tuple)
    def _handle_message_received(self, message_data: dict, addr: tuple):
        """处理接收到的消息"""
        try:
            message = Message.from_dict(message_data)
            
            # 保存到数据库
            self.db_manager.save_message(message)
            
            # 如果是当前聊天对象的消息，显示出来
            if self.current_chat_user and message.from_user_id == self.current_chat_user.user_id:
                self._display_message(message, is_mine=False)
            
            logger.info(f"收到来自 {message.from_username} 的消息")
            
        except Exception as e:
            logger.error(f"处理接收消息失败: {e}")
    
    def _display_message(self, message: Message, is_mine: bool = None):
        """显示消息"""
        if is_mine is None:
            is_mine = (message.from_user_id == self.user_manager.current_user.user_id)
        
        # 格式化时间
        time_str = datetime.fromtimestamp(message.timestamp).strftime("%H:%M:%S")
        
        # 格式化消息
        if is_mine:
            text = f'<div style="text-align: right; margin: 5px;">'
            text += f'<span style="color: #888;">{time_str}</span><br>'
            text += f'<span style="background-color: #e6f2ff; padding: 5px 10px; border-radius: 5px; display: inline-block;">{message.content}</span>'
            text += f'</div>'
        else:
            text = f'<div style="text-align: left; margin: 5px;">'
            text += f'<b>{message.from_username}</b> '
            text += f'<span style="color: #888;">{time_str}</span><br>'
            text += f'<span style="background-color: #f0f0f0; padding: 5px 10px; border-radius: 5px; display: inline-block;">{message.content}</span>'
            text += f'</div>'
        
        self.ui.messageDisplay.append(text)
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            self.broadcast_service.stop()
            self.message_service.stop()
            logger.info("应用程序已关闭")
        except Exception as e:
            logger.error(f"关闭应用失败: {e}")
        
        event.accept()
