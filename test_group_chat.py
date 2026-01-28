#!/usr/bin/env python3
"""
群组聊天功能测试脚本
"""
import sys
import time
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DatabaseManager
from src.core.group_manager import GroupManager
from src.utils.logger import get_logger


logger = get_logger(__name__)


def test_group_creation():
    """测试群组创建"""
    print("\n" + "="*50)
    print("测试1：群组创建")
    print("="*50)
    
    db = DatabaseManager()
    group_mgr = GroupManager(db_manager=db)
    
    try:
        group_mgr.start()
        
        # 创建群组
        group = group_mgr.create_group(
            group_name="测试群组",
            owner_id="user_001",
            member_ids=["user_002", "user_003"]
        )
        
        if group:
            print(f"✅ 群组创建成功:")
            print(f"   - 群组ID: {group.group_id}")
            print(f"   - 群组名: {group.group_name}")
            print(f"   - 组播地址: {group.multicast_ip}:{group.multicast_port}")
            print(f"   - 成员数: {len(group.member_ids)}")
            return group
        else:
            print("❌ 群组创建失败")
            return None
    finally:
        group_mgr.stop()


def test_group_message_multicast():
    """测试组播消息发送"""
    print("\n" + "="*50)
    print("测试2：组播消息发送（需要多个实例运行才能看到效果）")
    print("="*50)
    
    db = DatabaseManager()
    group_mgr = GroupManager(db_manager=db)
    
    received_messages = []
    
    def on_message(msg):
        print(f"📨 收到群组消息: {msg.from_username}: {msg.content}")
        received_messages.append(msg)
    
    group_mgr.on_group_message_received = on_message
    
    try:
        group_mgr.start()
        
        # 创建群组
        group = group_mgr.create_group(
            group_name="多播测试群",
            owner_id="user_test",
            member_ids=["user_002"]
        )
        
        if not group:
            print("❌ 群组创建失败")
            return
        
        print(f"✅ 群组已创建: {group.group_name}")
        print(f"   组播地址: {group.multicast_ip}:{group.multicast_port}")
        
        # 发送测试消息
        print("\n发送测试消息...")
        success = group_mgr.send_group_message(
            group_id=group.group_id,
            from_user_id="user_test",
            from_username="测试用户",
            content="Hello, Group! 这是一条组播消息"
        )
        
        if success:
            print("✅ 消息已通过组播发送")
        else:
            print("❌ 消息发送失败")
        
        # 等待接收（自己发的消息会被自己收到）
        print("\n等待消息接收（3秒）...")
        time.sleep(3)
        
        if received_messages:
            print(f"✅ 收到 {len(received_messages)} 条消息")
        else:
            print("⚠️ 未收到消息（可能因为是自己发的）")
        
        # 再发一条
        print("\n发送第二条消息...")
        group_mgr.send_group_message(
            group_id=group.group_id,
            from_user_id="user_test",
            from_username="测试用户",
            content="这是第二条消息"
        )
        
        time.sleep(2)
        
        # 检查数据库
        messages = db.get_group_messages(group.group_id)
        print(f"\n数据库中有 {len(messages)} 条群组消息")
        for msg in messages:
            print(f"   - {msg.from_username}: {msg.content}")
        
    finally:
        group_mgr.stop()
        db.close()


def test_database_operations():
    """测试数据库操作"""
    print("\n" + "="*50)
    print("测试3：数据库操作")
    print("="*50)
    
    db = DatabaseManager()
    
    # 测试保存群组
    from src.core.models import Group
    test_group = Group(
        group_id="test_group_001",
        group_name="数据库测试群",
        owner_id="owner_001",
        multicast_ip="239.0.0.100",
        multicast_port=10001,
        member_ids=["user_001", "user_002", "user_003"]
    )
    
    success = db.save_group(test_group)
    if success:
        print("✅ 群组保存成功")
    else:
        print("❌ 群组保存失败")
    
    # 测试读取群组
    retrieved = db.get_group("test_group_001")
    if retrieved:
        print(f"✅ 群组读取成功: {retrieved.group_name}")
        print(f"   成员: {retrieved.member_ids}")
    else:
        print("❌ 群组读取失败")
    
    # 测试添加成员
    db.add_group_member("test_group_001", "user_004")
    members = db.get_group_members("test_group_001")
    print(f"✅ 群组成员查询: 共 {len(members)} 人")
    
    db.close()


def main():
    """主函数"""
    print("\n" + "🚀 " * 20)
    print("群组聊天功能测试")
    print("🚀 " * 20)
    
    try:
        # 运行测试
        test_database_operations()
        test_group_creation()
        test_group_message_multicast()
        
        print("\n" + "="*50)
        print("✅ 所有测试完成！")
        print("="*50)
        
        print("\n💡 提示:")
        print("   - 要测试真实的组播通信，需要在不同终端启动多个程序实例")
        print("   - 确保防火墙允许 UDP 端口 10001")
        print("   - 组播地址范围：239.0.0.100 ~ 239.0.0.255")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
