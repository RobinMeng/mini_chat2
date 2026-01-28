#!/usr/bin/env python3
"""
快速验证脚本 - 检查所有导入和基本功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有导入"""
    print("测试导入...")
    try:
        from src.core.models import User, Message, Group
        print("✅ models.py 导入成功")
        
        from src.database.db_manager import DatabaseManager
        print("✅ db_manager.py 导入成功")
        
        from src.core.group_manager import GroupManager
        print("✅ group_manager.py 导入成功")
        
        from src.ui.backend import QmlBackend
        print("✅ backend.py 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_group_model():
    """测试 Group 模型"""
    print("\n测试 Group 模型...")
    try:
        from src.core.models import Group
        
        group = Group(
            group_id="test_001",
            group_name="测试群",
            owner_id="owner_001",
            multicast_ip="239.0.0.100",
            multicast_port=10001,
            member_ids=["user1", "user2"]
        )
        
        # 测试 to_dict
        data = group.to_dict()
        assert data['group_name'] == "测试群"
        
        # 测试 from_dict
        group2 = Group.from_dict(data)
        assert group2.group_id == "test_001"
        
        print("✅ Group 模型测试通过")
        return True
    except Exception as e:
        print(f"❌ Group 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库操作"""
    print("\n测试数据库操作...")
    try:
        from src.database.db_manager import DatabaseManager
        from src.core.models import Group
        
        db = DatabaseManager()
        
        # 测试保存群组
        test_group = Group(
            group_id="db_test_001",
            group_name="数据库测试群",
            owner_id="owner_001",
            multicast_ip="239.0.0.101",
            member_ids=["user1", "user2"]
        )
        
        success = db.save_group(test_group)
        assert success, "保存失败"
        
        # 测试读取群组
        retrieved = db.get_group("db_test_001")
        assert retrieved is not None, "读取失败"
        assert retrieved.group_name == "数据库测试群"
        
        # 测试成员操作
        db.add_group_member("db_test_001", "user3")
        
        db.close()
        print("✅ 数据库测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("群组聊天功能 - 快速验证")
    print("=" * 50)
    
    all_pass = True
    
    all_pass &= test_imports()
    all_pass &= test_group_model()
    all_pass &= test_database()
    
    print("\n" + "=" * 50)
    if all_pass:
        print("✅ 所有测试通过！核心功能正常。")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    print("=" * 50)

if __name__ == "__main__":
    main()
