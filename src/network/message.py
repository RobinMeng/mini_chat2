"""
TCP 消息服务 - 用于点对点消息传输
"""
import socket
import json
import threading
from typing import Callable, Optional
from src.config import config
from src.utils.logger import get_logger


logger = get_logger(__name__)


class MessageService:
    """TCP 消息服务类"""
    
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
        
    def start(self):
        """启动消息服务"""
        if self.running:
            logger.warning("消息服务已在运行")
            return
        
        self.running = True
        
        # 创建 TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', config.TCP_PORT))
        self.server_socket.listen(5)
        
        # 启动服务线程
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()
        
        logger.info(f"消息服务已启动，端口: {config.TCP_PORT}")
    
    def stop(self):
        """停止消息服务"""
        if not self.running:
            return
        
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
        
        if self.server_thread:
            self.server_thread.join(timeout=2)
        
        logger.info("消息服务已停止")
    
    def _server_loop(self):
        """服务器监听循环"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                # 为每个客户端连接创建新线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"接受连接失败: {e}")
    
    def _handle_client(self, client_socket: socket.socket, addr: tuple):
        """
        处理客户端连接
        
        Args:
            client_socket: 客户端 socket
            addr: 客户端地址
        """
        try:
            logger.info(f"接收到来自 {addr} 的连接")
            
            # 读取消息长度（前 4 字节）
            length_data = client_socket.recv(4)
            if not length_data:
                return
            
            msg_length = int.from_bytes(length_data, byteorder='big')
            
            # 读取完整消息
            message_data = b''
            while len(message_data) < msg_length:
                chunk = client_socket.recv(min(msg_length - len(message_data), 4096))
                if not chunk:
                    break
                message_data += chunk
            
            # 解析消息
            message_json = json.loads(message_data.decode('utf-8'))
            
            # 调用回调
            if self.on_message_received:
                self.on_message_received(message_json)
            
            logger.info(f"消息接收成功: {message_json.get('msg_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"处理客户端连接失败: {e}")
        finally:
            client_socket.close()
    
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
            
            # 序列化消息
            data = json.dumps(message).encode('utf-8')
            
            # 发送消息长度（前 4 字节）
            length_data = len(data).to_bytes(4, byteorder='big')
            client_socket.sendall(length_data)
            
            # 发送消息内容
            client_socket.sendall(data)
            
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
