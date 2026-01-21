"""
简单的网络功能测试
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import config
from src.utils.logger import setup_logger
from src.core import UserManager
from src.network import BroadcastService, MessageService
import time


def test_broadcast():
    """测试广播服务"""
    print("=" * 60)
    print("测试广播服务")
    print("=" * 60)
    
    # 初始化日志
    logger = setup_logger()
    
    # 初始化用户管理器
    user_manager = UserManager()
    current_user = user_manager.initialize_current_user("测试用户")
    
    print(f"当前用户: {current_user.username}")
    print(f"用户 ID: {current_user.user_id}")
    print(f"IP 地址: {current_user.ip_address}")
    print(f"TCP 端口: {current_user.tcp_port}")
    
    # 用户发现回调
    def on_user_discovered(user_data, addr):
        print(f"\n发现用户: {user_data.get('username')} ({addr[0]})")
    
    # 启动广播服务
    broadcast_service = BroadcastService(on_user_discovered=on_user_discovered)
    broadcast_service.set_current_user(current_user)
    broadcast_service.start()
    
    print("\n广播服务已启动，正在监听...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n停止服务...")
        broadcast_service.stop()
        print("服务已停止")


def test_message():
    """测试消息服务"""
    print("=" * 60)
    print("测试消息服务")
    print("=" * 60)
    
    # 初始化日志
    logger = setup_logger()
    
    # 消息接收回调
    def on_message_received(message_data):
        print(f"\n收到消息: {message_data.get('content')}")
        print(f"来自: {message_data.get('from_username')}")
    
    # 启动消息服务
    message_service = MessageService(on_message_received=on_message_received)
    message_service.start()
    
    print(f"\n消息服务已启动，监听端口: {config.TCP_PORT}")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n停止服务...")
        message_service.stop()
        print("服务已停止")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="网络功能测试")
    parser.add_argument(
        'test',
        choices=['broadcast', 'message', 'all'],
        help='测试类型: broadcast(广播), message(消息), all(全部)'
    )
    
    args = parser.parse_args()
    
    if args.test == 'broadcast':
        test_broadcast()
    elif args.test == 'message':
        test_message()
    elif args.test == 'all':
        print("启动完整测试...")
        print("请在另一个终端窗口运行相同的测试")
        test_broadcast()
