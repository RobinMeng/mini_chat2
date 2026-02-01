from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty
from src.core.models import User
from src.utils.logger import get_logger

logger = get_logger(__name__)

class UserController(QObject):
    """用户业务控制器"""
    userListChanged = pyqtSignal()
    currentUserChanged = pyqtSignal()

    def __init__(self, user_manager, db_manager):
        super().__init__()
        self.user_manager = user_manager
        self.db_manager = db_manager
        self._current_chat_user_id = None

    def set_current_chat_user_id(self, user_id):
        self._current_chat_user_id = user_id
        self.userListChanged.emit()

    @property
    def current_user(self):
        return self.user_manager.current_user

    def get_online_users_data(self):
        """供 QML 使用的用户列表数据格式化"""
        users = []
        current_me_id = self.current_user.user_id
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

    def handle_user_discovered(self, user_data: dict):
        """处理发现用户的回调"""
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
