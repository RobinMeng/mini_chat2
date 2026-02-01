from PyQt5.QtCore import QObject, pyqtSignal
from src.core.models import Group
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GroupController(QObject):
    """群组管理业务控制器"""
    groupListChanged = pyqtSignal()

    def __init__(self, group_manager, user_manager):
        super().__init__()
        self.group_manager = group_manager
        self.user_manager = user_manager
        self._current_chat_group_id = None

    def set_current_chat_group_id(self, group_id):
        self._current_chat_group_id = group_id
        self.groupListChanged.emit()

    def get_group_list_data(self):
        """格式化群组列表数据"""
        groups = []
        for group in self.group_manager.get_all_groups():
            groups.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'member_count': len(group.member_ids),
                'is_current': group.group_id == self._current_chat_group_id
            })
        return groups

    def create_group(self, group_name, member_user_ids):
        """执行创建群组操作"""
        try:
            group = self.group_manager.create_group(
                group_name=group_name,
                owner_id=self.user_manager.current_user.user_id,
                member_ids=member_user_ids
            )
            if group:
                self.groupListChanged.emit()
                return group
        except Exception as e:
            logger.error(f"GroupController 创建群组失败: {e}")
        return None

    def process_group_invite(self, invite_data: dict):
        """处理群组邀请逻辑 (UI 安全线程)"""
        try:
            target_ids = invite_data.get('target_user_ids', [])
            my_id = self.user_manager.current_user.user_id
            
            if my_id in target_ids or my_id == invite_data.get('owner_id'):
                group = Group(
                    group_id=invite_data.get('group_id'),
                    group_name=invite_data.get('group_name'),
                    owner_id=invite_data.get('owner_id'),
                    multicast_ip=invite_data.get('multicast_ip'),
                    multicast_port=invite_data.get('multicast_port', 10001),
                    member_ids=target_ids + [invite_data.get('owner_id')]
                )
                self.group_manager.join_group(group)
                self.groupListChanged.emit()
                return True
        except Exception as e:
            logger.error(f"GroupController 处理邀请失败: {e}")
        return False
