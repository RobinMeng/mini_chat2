"""
数据库管理器
"""
import sqlite3
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
            self.conn.close()
            logger.info("数据库连接已关闭")
    
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
