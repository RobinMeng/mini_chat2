"""
UDP 广播服务 - 用于用户发现
"""
import socket
import json
import time
import threading
from typing import Callable, Optional
from src.config import config
from src.utils.logger import get_logger


logger = get_logger(__name__)


class BroadcastService:
    """UDP 广播服务类"""
    
    def __init__(self, on_user_discovered: Optional[Callable] = None):
        """
        初始化广播服务
        
        Args:
            on_user_discovered: 发现用户时的回调函数
        """
        self.on_user_discovered = on_user_discovered
        self.socket = None
        self.running = False
        self.broadcast_thread = None
        self.listen_thread = None
        self.current_user = None  # 当前用户信息
    
    def set_current_user(self, user):
        """设置当前用户信息"""
        self.current_user = user
        
    def start(self):
        """启动广播服务"""
        if self.running:
            logger.warning("广播服务已在运行")
            return
        
        self.running = True
        
        # 创建 UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', config.BROADCAST_PORT))
        
        # 启动广播线程
        self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.broadcast_thread.start()
        
        # 启动监听线程
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        logger.info(f"广播服务已启动，端口: {config.BROADCAST_PORT}")
    
    def stop(self):
        """停止广播服务"""
        if not self.running:
            return
        
        self.running = False
        
        if self.socket:
            self.socket.close()
        
        if self.broadcast_thread:
            self.broadcast_thread.join(timeout=2)
        
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        
        logger.info("广播服务已停止")
    
    def _broadcast_loop(self):
        """广播循环"""
        while self.running:
            try:
                self._send_heartbeat()
                time.sleep(config.BROADCAST_INTERVAL)
            except Exception as e:
                logger.error(f"广播发送失败: {e}")
    
    def _listen_loop(self):
        """监听循环"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                self._handle_received_data(data, addr)
            except Exception as e:
                if self.running:
                    logger.error(f"接收广播失败: {e}")
    
    def _send_heartbeat(self):
        """发送心跳包"""
        try:
            if not self.current_user:
                return
            
            heartbeat = {
                'type': 'HEARTBEAT',
                'version': '1.0',
                'user_id': self.current_user.user_id,
                'username': self.current_user.username,
                'hostname': self.current_user.hostname,
                'ip': self.current_user.ip_address,
                'tcp_port': self.current_user.tcp_port,
                'timestamp': int(time.time())
            }
            
            data = json.dumps(heartbeat).encode('utf-8')
            self.socket.sendto(data, (config.BROADCAST_ADDRESS, config.BROADCAST_PORT))
            logger.debug("心跳包已发送")
            
        except Exception as e:
            logger.error(f"发送心跳包失败: {e}")
    
    def _handle_received_data(self, data: bytes, addr: tuple):
        """
        处理接收到的数据
        
        Args:
            data: 接收到的数据
            addr: 发送方地址
        """
        try:
            message = json.loads(data.decode('utf-8'))
            
            if self.on_user_discovered and message.get('type') == 'HEARTBEAT':
                self.on_user_discovered(message, addr)
                
        except Exception as e:
            logger.error(f"处理广播数据失败: {e}")
