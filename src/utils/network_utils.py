"""
网络通信工具类
封装通用的 TCP 数据收发逻辑
"""
import json
import socket
from typing import Optional, Dict, Any, List


def send_json(sock: socket.socket, data: Dict[str, Any]) -> None:
    """
    发送 JSON 数据，采用 4 字节长度前缀协议
    
    Args:
        sock: 已连接的 socket 对象
        data: 要发送的字典数据
    """
    json_str = json.dumps(data).encode('utf-8')
    # 发送消息长度（前 4 字节，大端字节序）
    length_data = len(json_str).to_bytes(4, byteorder='big')
    sock.sendall(length_data)
    # 发送消息内容
    sock.sendall(json_str)


def receive_json(sock: socket.socket) -> Optional[Dict[str, Any]]:
    """
    接收 JSON 数据（阻塞模式），复用协议逻辑
    """
    try:
        # 1. 读取长度前缀
        length_data = b''
        while len(length_data) < 4:
            chunk = sock.recv(4 - len(length_data))
            if not chunk: return None
            length_data += chunk
        
        msg_length = int.from_bytes(length_data, byteorder='big')
        
        # 2. 读取完整内容
        message_data = b''
        while len(message_data) < msg_length:
            chunk = sock.recv(min(msg_length - len(message_data), 4096))
            if not chunk: break
            message_data += chunk
            
        if len(message_data) < msg_length: return None
            
        # 3. 解析 JSON
        return json.loads(message_data.decode('utf-8'))
    except:
        return None


def unpack_json(buffer: bytearray) -> Optional[Dict[str, Any]]:
    """
    从字节缓冲区尝试解析一条 JSON 消息 (4字节长度前缀协议)
    
    Args:
        buffer: 字节缓冲区 (bytearray)
        
    Returns:
        解析后的字典数据。如果解析成功，会从 buffer 中移除已处理的数据；
        如果数据不完整，返回 None 且不修改 buffer。
    """
    if len(buffer) < 4:
        return None
    
    # 读取长度前缀（不修改 buffer）
    msg_length = int.from_bytes(buffer[:4], byteorder='big')
    
    # 检查内容是否接收完整
    if len(buffer) < 4 + msg_length:
        return None
    
    try:
        # 提取数据并从缓冲区移除
        msg_data = buffer[4:4+msg_length]
        del buffer[:4+msg_length]
        
        return json.loads(msg_data.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # 解析失败也要移除坏数据，防止阻塞后续消息
        del buffer[:4+msg_length]
        return None


def read_and_unpack(sock: socket.socket, buffer: bytearray) -> Optional[List[Dict[str, Any]]]:
    """
    处理非阻塞读事件：从 socket 读取数据并解析出所有完整的 JSON 消息
    
    Args:
        sock: socket 对象
        buffer: 该连接对应的字节缓冲区
        
    Returns:
        解析出的消息列表。如果连接已关闭或出错返回 None
    """
    try:
        data = sock.recv(4096)
        if not data:
            return None # 连接已关闭
            
        buffer.extend(data)
        messages = []
        while True:
            msg = unpack_json(buffer)
            if msg is None:
                break
            messages.append(msg)
        return messages
    except BlockingIOError:
        # 非阻塞模式下资源暂时不可用
        return []
    except Exception:
        # 其他 socket 错误视为连接失效
        return None
