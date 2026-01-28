"""
数据库管理器
"""
import os
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from src.config import config
from src.utils.logger import get_logger


logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.db_path = config.DB_PATH
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect()
        self.init_tables()
        
    def connect(self):
        """连接数据库"""
        try:
            # 确保数据目录存在
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 使查询结果可以按列名访问
            self.cursor = self.conn.cursor()
            
            logger.info(f"数据库已连接: {self.db_path}")
            
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                self.cursor = None
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库失败: {e}")

    def destroy(self):
        """彻底销毁数据库（阅后即焚）"""
        self.close()
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                logger.info(f"数据库文件已物理删除: {self.db_path}")
        except Exception as e:
            logger.error(f"删除数据库文件失败: {e}")
    
    def init_tables(self):
        """初始化数据库表"""
        try:
            # 用户表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    hostname TEXT,
                    ip_address TEXT,
                    tcp_port INTEGER,
                    status TEXT DEFAULT 'offline',
                    last_seen INTEGER,
                    avatar TEXT,
                    created_at INTEGER,
                    updated_at INTEGER
                )
            ''')
            
            # 消息表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    msg_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    from_user_id TEXT NOT NULL,
                    from_username TEXT,
                    to_user_id TEXT NOT NULL,
                    to_username TEXT,
                    content TEXT,
                    timestamp INTEGER,
                    is_group INTEGER DEFAULT 0,
                    group_id TEXT,
                    is_read INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'sent',
                    created_at INTEGER,
                    FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (to_user_id) REFERENCES users(user_id)
                )
            ''')
            
            # 文件传输记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_transfers (
                    file_id TEXT PRIMARY KEY,
                    from_user_id TEXT NOT NULL,
                    to_user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    filesize INTEGER,
                    file_type TEXT,
                    checksum TEXT,
                    save_path TEXT,
                    chunk_size INTEGER,
                    total_chunks INTEGER,
                    transferred_chunks INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    start_time INTEGER,
                    end_time INTEGER,
                    created_at INTEGER,
                    FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (to_user_id) REFERENCES users(user_id)
                )
            ''')
            
            # 群组表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id TEXT PRIMARY KEY,
                    group_name TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    multicast_ip TEXT NOT NULL,
                    multicast_port INTEGER DEFAULT 10001,
                    member_ids TEXT,
                    created_at INTEGER,
                    updated_at INTEGER,
                    avatar TEXT,
                    description TEXT,
                    FOREIGN KEY (owner_id) REFERENCES users(user_id)
                )
            ''')
            
            # 群组成员表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at INTEGER,
                    FOREIGN KEY (group_id) REFERENCES groups(group_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(group_id, user_id)
                )
            ''')
            
            # 设置表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at INTEGER
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_from_user ON messages(from_user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_to_user ON messages(to_user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id)')
            
            self.conn.commit()
            logger.info("数据库表初始化完成")
            
        except Exception as e:
            logger.error(f"初始化数据库表失败: {e}")
            raise
    
    def execute(self, sql: str, params: tuple = None) -> bool:
        """
        执行 SQL 语句
        
        Args:
            sql: SQL 语句
            params: 参数元组
        
        Returns:
            是否成功
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"执行 SQL 失败: {e}")
            self.conn.rollback()
            return False
    
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        查询数据
        
        Args:
            sql: SQL 语句
            params: 参数元组
        
        Returns:
            查询结果列表
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []
    
    def query_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        查询单条数据
        
        Args:
            sql: SQL 语句
            params: 参数元组
        
        Returns:
            查询结果字典，不存在返回 None
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return None

    def save_message(self, message):
        """保存消息到数据库"""
        sql = '''
            INSERT INTO messages (
                msg_id, type, from_user_id, from_username,
                to_user_id, to_username, content, timestamp,
                is_group, group_id, is_read, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            message.msg_id, message.type, message.from_user_id, message.from_username,
            message.to_user_id, message.to_username, message.content, message.timestamp,
            1 if message.is_group else 0, message.group_id, 1 if message.is_read else 0,
            message.status, int(time.time())
        )
        return self.execute(sql, params)

    def get_messages(self, user1_id, user2_id, limit=50):
        """获取两个用户之间的聊天历史"""
        from src.core.models import Message
        sql = '''
            SELECT * FROM messages 
            WHERE (from_user_id = ? AND to_user_id = ?) 
               OR (from_user_id = ? AND to_user_id = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        params = (user1_id, user2_id, user2_id, user1_id, limit)
        rows = self.query(sql, params)
        
        # 转换回 Message 对象列表，并按时间正序排列（QML 通常从旧到新显示）
        messages = [Message.from_dict(row) for row in rows]
        messages.reverse()
        return messages

    def get_unread_count(self, from_user_id, to_user_id):
        """获取来自特定用户的未读消息数量"""
        sql = '''
            SELECT COUNT(*) as count FROM messages 
            WHERE from_user_id = ? AND to_user_id = ? AND is_read = 0
        '''
        params = (from_user_id, to_user_id)
        result = self.query_one(sql, params)
        return result['count'] if result else 0

    def mark_as_read(self, from_user_id, to_user_id):
        """将来自特定用户的所有未读消息标记为已读"""
        sql = '''
            UPDATE messages 
            SET is_read = 1 
            WHERE from_user_id = ? AND to_user_id = ? AND is_read = 0
        '''
        params = (from_user_id, to_user_id)
        return self.execute(sql, params)

    def save_group(self, group):
        """保存群组到数据库"""
        import json
        sql = '''
            INSERT OR REPLACE INTO groups (
                group_id, group_name, owner_id, multicast_ip, multicast_port,
                member_ids, created_at, updated_at, avatar, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            group.group_id, group.group_name, group.owner_id,
            group.multicast_ip, group.multicast_port,
            json.dumps(group.member_ids), group.created_at, group.updated_at,
            group.avatar, group.description
        )
        return self.execute(sql, params)

    def get_group(self, group_id):
        """获取群组信息"""
        from src.core.models import Group
        sql = 'SELECT * FROM groups WHERE group_id = ?'
        result = self.query_one(sql, (group_id,))
        return Group.from_dict(result) if result else None

    def get_all_groups(self):
        """获取当前用户加入的所有群组"""
        from src.core.models import Group
        sql = 'SELECT * FROM groups ORDER BY updated_at DESC'
        rows = self.query(sql)
        return [Group.from_dict(row) for row in rows]

    def add_group_member(self, group_id, user_id, role='member'):
        """添加群组成员"""
        sql = '''
            INSERT OR IGNORE INTO group_members (group_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        '''
        params = (group_id, user_id, role, int(time.time()))
        return self.execute(sql, params)

    def remove_group_member(self, group_id, user_id):
        """移除群组成员"""
        sql = 'DELETE FROM group_members WHERE group_id = ? AND user_id = ?'
        return self.execute(sql, (group_id, user_id))

    def get_group_members(self, group_id):
        """获取群组成员列表"""
        sql = '''
            SELECT u.* FROM users u
            INNER JOIN group_members gm ON u.user_id = gm.user_id
            WHERE gm.group_id = ?
        '''
        rows = self.query(sql, (group_id,))
        from src.core.models import User
        return [User.from_dict(row) for row in rows]

    def get_group_messages(self, group_id, limit=50):
        """获取群组消息历史"""
        from src.core.models import Message
        sql = '''
            SELECT * FROM messages 
            WHERE group_id = ? AND is_group = 1
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        rows = self.query(sql, (group_id, limit))
        messages = [Message.from_dict(row) for row in rows]
        messages.reverse()
        return messages
