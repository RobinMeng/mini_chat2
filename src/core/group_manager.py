"""
群组管理器 - 纯组播方案实现
"""
import socket
import struct
import threading
import json
import uuid
import time
from typing import Callable, Optional, Dict, List
from src.core.models import Group, Message
from src.utils.logger import get_logger


logger = get_logger(__name__)


class GroupManager:
    """群组管理器类（基于 UDP 组播）"""
    
    # 组播地址池（239.0.0.100 ~ 239.0.0.255）
    MULTICAST_BASE = "239.0.0"
    MULTICAST_START = 100
    MULTICAST_END = 255
    MULTICAST_PORT = 10001
    
    def __init__(self, db_manager, on_group_message_received: Optional[Callable] = None, on_broadcast_needed: Optional[Callable] = None):
        """
        初始化群组管理器
        
        Args:
            db_manager: 数据库管理器实例
            on_group_message_received: 接收到群组消息时的回调
            on_broadcast_needed: 需要发送广播时的回调（用于发送群组邀请）
        """
        self.db_manager = db_manager
        self.on_group_message_received = on_group_message_received
        self.on_broadcast_needed = on_broadcast_needed
        
        # 群组 ID -> Group 对象
        self.groups: Dict[str, Group] = {}
        
        # 群组 ID -> 组播 socket
        self.multicast_sockets: Dict[str, socket.socket] = {}
        
        # 监听线程
        self.listen_threads: Dict[str, threading.Thread] = {}
        
        # 运行状态
        self.running = False
        
        # 已分配的组播地址（用于避免冲突）
        self.allocated_ips = set()
        
    def start(self):
        """启动群组管理器"""
        if self.running:
            logger.warning("群组管理器已在运行")
            return
        
        self.running = True
        
        # 从数据库加载所有群组
        self._load_groups_from_db()
        
        # 为每个群组启动监听
        for group_id in self.groups.keys():
            self._start_group_listener(group_id)
        
        logger.info(f"群组管理器已启动，已加载 {len(self.groups)} 个群组")
    
    def stop(self):
        """停止群组管理器"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止所有监听线程并关闭 socket
        for group_id in list(self.multicast_sockets.keys()):
            self._stop_group_listener(group_id)
        
        logger.info("群组管理器已停止")
    
    def _load_groups_from_db(self):
        """从数据库加载群组"""
        groups = self.db_manager.get_all_groups()
        for group in groups:
            self.groups[group.group_id] = group
            self.allocated_ips.add(group.multicast_ip)
    
    def _allocate_multicast_ip(self) -> str:
        """分配一个未使用的组播地址"""
        for i in range(self.MULTICAST_START, self.MULTICAST_END + 1):
            ip = f"{self.MULTICAST_BASE}.{i}"
            if ip not in self.allocated_ips:
                self.allocated_ips.add(ip)
                return ip
        raise RuntimeError("组播地址池已满，无法分配新地址")
    
    def _generate_group_id(self) -> str:
        """生成唯一的群组 ID"""
        return f"group_{uuid.uuid4().hex[:12]}"
    
    def create_group(self, group_name: str, owner_id: str, member_ids: List[str]) -> Optional[Group]:
        """
        创建群组
        
        Args:
            group_name: 群组名称
            owner_id: 创建者 ID
            member_ids: 成员 ID 列表（不包含创建者）
        
        Returns:
            创建的群组对象，失败返回 None
        """
        try:
            # 生成群组 ID 和分配组播地址
            group_id = self._generate_group_id()
            multicast_ip = self._allocate_multicast_ip()
            
            # 成员列表包含创建者
            all_members = [owner_id] + [m for m in member_ids if m != owner_id]
            
            # 创建群组对象
            group = Group(
                group_id=group_id,
                group_name=group_name,
                owner_id=owner_id,
                multicast_ip=multicast_ip,
                multicast_port=self.MULTICAST_PORT,
                member_ids=all_members
            )
            
            # 保存到数据库
            if not self.db_manager.save_group(group):
                logger.error(f"保存群组失败: {group_id}")
                self.allocated_ips.discard(multicast_ip)
                return None
            
            # 保存成员关系
            self.db_manager.add_group_member(group_id, owner_id, role='owner')
            for member_id in member_ids:
                self.db_manager.add_group_member(group_id, member_id, role='member')
            
            # 加入内存管理
            self.groups[group_id] = group
            
            # 启动组播监听
            self._start_group_listener(group_id)
            
            # 发送群组邀请广播
            self.send_group_invite(group_id, owner_id, member_ids)
            
            logger.info(f"群组创建成功: {group_name} ({group_id}), 组播地址: {multicast_ip}")
            return group
            
        except Exception as e:
            logger.error(f"创建群组失败: {e}")
            return None
    
    def join_group(self, group: Group):
        """
        加入群组（订阅组播组）
        
        Args:
            group: 群组对象
        """
        if group.group_id in self.groups:
            logger.warning(f"已经加入群组: {group.group_id}")
            return
        
        # 保存到数据库
        self.db_manager.save_group(group)
        
        # 加入内存管理
        self.groups[group.group_id] = group
        self.allocated_ips.add(group.multicast_ip)
        
        # 启动组播监听
        self._start_group_listener(group.group_id)
        
        logger.info(f"已加入群组: {group.group_name} ({group.group_id})")
    
    def leave_group(self, group_id: str):
        """
        退出群组
        
        Args:
            group_id: 群组 ID
        """
        if group_id not in self.groups:
            logger.warning(f"未加入该群组: {group_id}")
            return
        
        # 停止监听
        self._stop_group_listener(group_id)
        
        # 从内存中移除
        group = self.groups.pop(group_id)
        self.allocated_ips.discard(group.multicast_ip)
        
        logger.info(f"已退出群组: {group_id}")
    
    def _start_group_listener(self, group_id: str):
        """启动群组的组播监听"""
        if group_id not in self.groups:
            logger.error(f"群组不存在: {group_id}")
            return
        
        if group_id in self.multicast_sockets:
            logger.warning(f"群组监听已启动: {group_id}")
            return
        
        group = self.groups[group_id]
        
        try:
            # 创建 UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # macOS 需要设置 SO_REUSEPORT
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except AttributeError:
                pass
            
            # 绑定到组播端口
            sock.bind(('', group.multicast_port))
            
            # 加入组播组
            mreq = struct.pack("4sl", socket.inet_aton(group.multicast_ip), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            # 设置超时，以便能响应停止信号
            sock.settimeout(1.0)
            
            # 保存 socket
            self.multicast_sockets[group_id] = sock
            
            # 启动监听线程
            thread = threading.Thread(target=self._listen_loop, args=(group_id,), daemon=True)
            thread.start()
            self.listen_threads[group_id] = thread
            
            logger.info(f"群组监听已启动: {group.group_name} ({group.multicast_ip}:{group.multicast_port})")
            
        except Exception as e:
            logger.error(f"启动群组监听失败: {e}")
    
    def _stop_group_listener(self, group_id: str):
        """停止群组的组播监听"""
        # 关闭 socket
        if group_id in self.multicast_sockets:
            try:
                sock = self.multicast_sockets[group_id]
                group = self.groups.get(group_id)
                
                if group:
                    # 离开组播组
                    mreq = struct.pack("4sl", socket.inet_aton(group.multicast_ip), socket.INADDR_ANY)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
                
                sock.close()
            except:
                pass
            del self.multicast_sockets[group_id]
        
        # 等待线程结束
        if group_id in self.listen_threads:
            thread = self.listen_threads[group_id]
            thread.join(timeout=2)
            del self.listen_threads[group_id]
    
    def _listen_loop(self, group_id: str):
        """组播监听循环"""
        sock = self.multicast_sockets.get(group_id)
        if not sock:
            return
        
        logger.info(f"组播监听线程启动: {group_id}")
        
        while self.running and group_id in self.multicast_sockets:
            try:
                data, addr = sock.recvfrom(65535)
                self._handle_multicast_data(group_id, data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"接收组播消息失败 ({group_id}): {e}")
        
        logger.info(f"组播监听线程退出: {group_id}")
    
    def _handle_multicast_data(self, group_id: str, data: bytes, addr: tuple):
        """
        处理接收到的组播数据
        
        Args:
            group_id: 群组 ID
            data: 接收到的数据
            addr: 发送方地址
        """
        try:
            payload = json.loads(data.decode('utf-8'))
            msg_type = payload.get('type')
            
            if msg_type == 'GROUP_MESSAGE':
                # 构建 Message 对象
                message = Message(
                    msg_id=payload.get('msg_id'),
                    type=payload.get('msg_type', 'TEXT'),
                    from_user_id=payload.get('from_user_id'),
                    from_username=payload.get('from_username'),
                    to_user_id='',  # 群组消息不需要
                    content=payload.get('content'),
                    timestamp=payload.get('timestamp', int(time.time())),
                    is_group=True,
                    group_id=group_id
                )
                
                # 保存到数据库
                self.db_manager.save_message(message)
                
                # 触发回调
                if self.on_group_message_received:
                    self.on_group_message_received(message)
                
                logger.info(f"收到群组消息: {group_id} from {message.from_username}")
            
            elif msg_type == 'GROUP_INVITE':
                # 处理群组邀请（接收端）
                logger.info(f"收到群组邀请: {payload}")
                # TODO: 通知 UI 显示邀请通知
            
        except Exception as e:
            logger.error(f"处理组播数据失败: {e}")
    
    def send_group_message(self, group_id: str, from_user_id: str, from_username: str, content: str) -> bool:
        """
        发送群组消息（组播）
        
        Args:
            group_id: 群组 ID
            from_user_id: 发送者 ID
            from_username: 发送者用户名
            content: 消息内容
        
        Returns:
            是否发送成功
        """
        if group_id not in self.groups:
            logger.error(f"群组不存在: {group_id}")
            return False
        
        group = self.groups[group_id]
        
        try:
            # 构建消息负载
            msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            payload = {
                'type': 'GROUP_MESSAGE',
                'msg_id': msg_id,
                'msg_type': 'TEXT',
                'group_id': group_id,
                'from_user_id': from_user_id,
                'from_username': from_username,
                'content': content,
                'timestamp': int(time.time())
            }
            
            # 创建临时 socket 发送
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            
            data = json.dumps(payload).encode('utf-8')
            sock.sendto(data, (group.multicast_ip, group.multicast_port))
            sock.close()
            
            # 保存自己的消息到数据库
            message = Message(
                msg_id=msg_id,
                type='TEXT',
                from_user_id=from_user_id,
                from_username=from_username,
                to_user_id='',
                content=content,
                timestamp=payload['timestamp'],
                is_group=True,
                group_id=group_id,
                status='sent'
            )
            self.db_manager.save_message(message)
            
            logger.info(f"群组消息已发送: {group.group_name} -> {content[:20]}")
            return True
            
        except Exception as e:
            logger.error(f"发送群组消息失败: {e}")
            return False
    
    def send_group_invite(self, group_id: str, inviter_id: str, target_user_ids: List[str]):
        """
        发送群组邀请（通过组播）
        
        Args:
            group_id: 群组 ID
            inviter_id: 邀请人 ID
            target_user_ids: 被邀请人 ID 列表
        """
        if group_id not in self.groups:
            logger.error(f"群组不存在: {group_id}")
            return
        
        group = self.groups[group_id]
        
        try:
            payload = {
                'type': 'GROUP_INVITE',
                'group_id': group_id,
                'group_name': group.group_name,
                'multicast_ip': group.multicast_ip,
                'multicast_port': group.multicast_port,
                'owner_id': group.owner_id,
                'inviter_id': inviter_id,
                'target_user_ids': target_user_ids,
                'timestamp': int(time.time())
            }
            
            # 使用广播服务发送邀请，这样所有人都能在发现频道收到
            if self.on_broadcast_needed:
                self.on_broadcast_needed(payload)
                logger.info(f"群组邀请广播已提交: {group.group_name}")
            else:
                # 降级：通过组播尝试（可能由于还没加入而收不到）
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
                data = json.dumps(payload).encode('utf-8')
                sock.sendto(data, (group.multicast_ip, group.multicast_port))
                sock.close()
                logger.info(f"群组邀请组播已发送 (降级模式): {group.group_name}")
            
        except Exception as e:
            logger.error(f"发送群组邀请失败: {e}")
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """获取群组对象"""
        return self.groups.get(group_id)
    
    def get_all_groups(self) -> List[Group]:
        """获取所有群组列表"""
        return list(self.groups.values())
