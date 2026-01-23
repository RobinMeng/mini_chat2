"""
TCP 消息服务 - 用于点对点消息传输
"""
import socket
import threading
import selectors
import json
from typing import Callable, Optional, Dict
from src.config import config
from src.utils.logger import get_logger
from src.utils.network_utils import send_json, read_and_unpack


logger = get_logger(__name__)


class MessageService:
    """TCP 消息服务类 (基于 selectors 实现多路复用)"""
    
    def __init__(self, on_message_received: Optional[Callable] = None):
        """
        初始化消息服务
        
        Args:
            on_message_received: 接收到消息时的回调函数
        """
        self.on_message_received = on_message_received
        self.server_socket = None
        self.running = False
        self.server_thread = None
        self.selector = selectors.DefaultSelector()
        self._client_buffers: Dict[socket.socket, bytearray] = {}
        
    def start(self):
        """启动消息服务"""
        if self.running:
            logger.warning("消息服务已在运行")
            return
        
        self.running = True
        
        try:
            # 创建 TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setblocking(False)  # 设置为非阻塞
            self.server_socket.bind(('', config.TCP_PORT))
            self.server_socket.listen(100)  # 增加监听队列
            
            # 注册服务器 socket 到 selector
            self.selector.register(self.server_socket, selectors.EVENT_READ, self._accept)
            
            # 启动服务线程
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            logger.info(f"消息服务已启动 (多路复用模式)，端口: {config.TCP_PORT}")
        except Exception as e:
            self.running = False
            logger.error(f"启动消息服务失败: {e}")
            raise
    
    def stop(self):
        """停止消息服务"""
        if not self.running:
            return
        
        self.running = False
        
        # 关闭所有客户端连接
        for sock in list(self._client_buffers.keys()):
            self._close_client(sock)
            
        if self.server_socket:
            self.selector.unregister(self.server_socket)
            self.server_socket.close()
        
        self.selector.close()
        
        if self.server_thread:
            self.server_thread.join(timeout=2)
        
        logger.info("消息服务已停止")
    
    def _server_loop(self):
        """服务器监听循环"""
        while self.running:
            try:
                # 等待 I/O 事件，设置超时以便能响应停止信号
                events = self.selector.select(timeout=1)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
            except Exception as e:
                if self.running:
                    logger.error(f"Selector 循环出错: {e}")
    
    def _accept(self, sock, mask):
        """处理新连接"""
        try:
            client_socket, addr = sock.accept()
            logger.info(f"接收到来自 {addr} 的连接")
            client_socket.setblocking(False)
            self._client_buffers[client_socket] = bytearray()
            # 注册客户端 socket 监听读事件
            self.selector.register(client_socket, selectors.EVENT_READ, self._read)
        except Exception as e:
            logger.error(f"接受连接失败: {e}")

    def _read(self, client_socket, mask):
        """处理读数据"""
        buf = self._client_buffers[client_socket]
        messages = read_and_unpack(client_socket, buf)
        
        if messages is None:
            # 连接已关闭
            self._close_client(client_socket)
        else:
            # 处理解析出的消息
            for msg in messages:
                if self.on_message_received:
                    self.on_message_received(msg)
                    logger.info(f"消息接收成功: {msg.get('msg_id', 'unknown')}")

    def _close_client(self, client_socket):
        """关闭客户端连接并清理资源"""
        try:
            self.selector.unregister(client_socket)
            client_socket.close()
        except:
            pass
        if client_socket in self._client_buffers:
            del self._client_buffers[client_socket]
    
    def send_message(self, target_ip: str, target_port: int, message: dict) -> bool:
        """
        发送消息到目标用户
        
        Args:
            target_ip: 目标 IP 地址
            target_port: 目标端口
            message: 消息内容（字典）
        
        Returns:
            是否发送成功
        """
        client_socket = None
        try:
            # 创建客户端 socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # 设置超时
            client_socket.connect((target_ip, target_port))
            
            # 使用工具函数发送 JSON 消息
            send_json(client_socket, message)
            
            logger.info(f"消息已发送到 {target_ip}:{target_port}")
            return True
            
        except socket.timeout:
            logger.error(f"连接超时: {target_ip}:{target_port}")
            return False
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
        finally:
            if client_socket:
                client_socket.close()
