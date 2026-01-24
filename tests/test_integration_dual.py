import os
import sys
import time
import multiprocessing
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.core import UserManager
from src.network import BroadcastService, MessageService
from src.utils.logger import setup_logger

def run_chat_node(name, data_dir, tcp_port, udp_port, target_queue, result_queue):
    """
    运行一个独立的聊天节点进程
    """
    # 强制设置环境变量以隔离配置
    os.environ["MINICHAT_DATA_DIR"] = data_dir
    os.environ["MINICHAT_TCP_PORT"] = str(tcp_port)
    os.environ["MINICHAT_UDP_PORT"] = str(udp_port)
    
    # 延迟加载 config 以确保读取到最新的环境变量
    from src.config import config
    
    # 初始化
    logger = setup_logger()
    user_manager = UserManager()
    current_user = user_manager.initialize_current_user(name)
    
    received_messages = []
    discovered_users = []

    # 回调函数
    def on_user_discovered(user_data, addr):
        discovered_users.append(user_data)
        print(f"[{name}] 发现邻居: {user_data['username']} @ {addr[0]}")

    def on_message_received(msg_data):
        received_messages.append(msg_data)
        print(f"[{name}] 收到来自 {msg_data['from_username']} 的消息: {msg_data['content']}")

    # 启动网络服务
    msg_service = MessageService(on_message_received=on_message_received)
    msg_service.start()
    
    bc_service = BroadcastService(on_user_discovered=on_user_discovered)
    bc_service.set_current_user(current_user)
    bc_service.start()

    print(f"[{name}] 服务已就绪 (TCP:{tcp_port}, UDP:{udp_port})")

    # 简单的事件循环处理指令
    try:
        while True:
            # 检查是否有发送任务
            if not target_queue.empty():
                cmd = target_queue.get()
                if cmd["type"] == "SEND":
                    # 获取目标用户信息（从发现列表中找）
                    target_user = next((u for u in discovered_users if u['username'] == cmd['to']), None)
                    if target_user:
                        msg_service.send_message(
                            target_user['ip'], 
                            target_user['port'], 
                            cmd['content'],
                            from_user_id=current_user.user_id,
                            from_username=current_user.username
                        )
                    else:
                        print(f"[{name}] 错误: 尚未发现用户 {cmd['to']}")
                elif cmd["type"] == "EXIT":
                    break
            
            # 向主进程汇报状态
            status = {
                "name": name,
                "discovered_count": len(discovered_users),
                "received_messages": received_messages.copy()
            }
            result_queue.put(status)
            time.sleep(0.5)
    finally:
        bc_service.stop()
        msg_service.stop()

if __name__ == "__main__":
    print("🚀 启动全自动双机通讯集成测试...")
    
    # 清理旧的测试数据
    import shutil
    for d in ["test_data_A", "test_data_B"]:
        if os.path.exists(d): shutil.rmtree(d)

    # 创建通信队列
    q_to_a = multiprocessing.Queue()
    q_to_b = multiprocessing.Queue()
    q_results = multiprocessing.Queue()

    # 启动两个节点
    p_a = multiprocessing.Process(target=run_chat_node, args=("User_A", "test_data_A", 10001, 9999, q_to_a, q_results))
    p_b = multiprocessing.Process(target=run_chat_node, args=("User_B", "test_data_B", 10002, 9999, q_to_b, q_results))

    p_a.start()
    p_b.start()

    success = False
    try:
        print("\n1. 等待双方互相发现 (预计 5-10 秒)...")
        timeout = 20
        start_time = time.time()
        a_found_b = False
        b_found_a = False

        while time.time() - start_time < timeout:
            while not q_results.empty():
                res = q_results.get()
                if res["name"] == "User_A" and res["discovered_count"] > 0: a_found_b = True
                if res["name"] == "User_B" and res["discovered_count"] > 0: b_found_a = True
            
            if a_found_b and b_found_a:
                print("✅ 双方已互相发现！")
                break
            time.sleep(1)
        else:
            print("❌ 超时：双方未能互相发现。检查防火墙或 UDP 广播设置。")
            sys.exit(1)

        print("\n2. 测试消息传递 (A -> B)...")
        q_to_a.put({"type": "SEND", "to": "User_B", "content": "你好，我是 A！"})
        
        time.sleep(2)
        
        print("\n3. 测试消息回复 (B -> A)...")
        q_to_b.put({"type": "SEND", "to": "User_A", "content": "收到，A！我是 B。"})

        time.sleep(2)

        # 验证最终结果
        final_messages_a = []
        final_messages_b = []
        while not q_results.empty():
            res = q_results.get()
            if res["name"] == "User_A": final_messages_a = res["received_messages"]
            if res["name"] == "User_B": final_messages_b = res["received_messages"]

        if any(m["content"] == "收到，A！我是 B。" for m in final_messages_a) and \
           any(m["content"] == "你好，我是 A！" for m in final_messages_b):
            print("\n" + "★" * 30)
            print("  ✨ 集成测试圆满成功！ ✨")
            print("  双方已完成：发现 + 双向通讯")
            print("★" * 30)
            success = True
        else:
            print("\n❌ 消息验证失败：部分消息未送达。")

    finally:
        print("\n正在关闭测试节点...")
        q_to_a.put({"type": "EXIT"})
        q_to_b.put({"type": "EXIT"})
        p_a.join(timeout=2)
        p_b.join(timeout=2)
        if p_a.is_alive(): p_a.terminate()
        if p_b.is_alive(): p_b.terminate()
        print("测试结束。")
