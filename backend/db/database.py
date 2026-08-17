import sqlite3
import os

DB_PATH = os.getenv("DATABASE_PATH", "./db/mikeross.db")

def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    conn.row_factory = sqlite3.Row
    
    return conn

def init_db():
    """
    Initializes the database schema by creating required tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    #'users' table (Section 5.1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            timezone TEXT NOT NULL DEFAULT 'UTC',
            default_priority TEXT DEFAULT 'medium',
            default_tags TEXT DEFAULT '[]'
        )
    ''')

    # 'captures' table (Section 5.2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS captures (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            capture_type TEXT NOT NULL CHECK (capture_type IN ('screenshot','voice','text')),
            item_type TEXT NOT NULL CHECK (item_type IN ('task','event','unknown')),
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            due_time TEXT,
            duration_minutes INTEGER,
            tags TEXT DEFAULT '[]',
            subtasks TEXT DEFAULT '[]',
            assignee TEXT,
            confidence REAL NOT NULL,
            reasoning TEXT,
            raw_input_ref TEXT,
            synced_to_calendar BOOLEAN DEFAULT FALSE,
            synced_to_todoist BOOLEAN DEFAULT FALSE,
            calendar_event_id TEXT,
            todoist_task_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 'oauth_tokens' table (Section 5.3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            service TEXT NOT NULL CHECK (service IN ('google','todoist')),
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 'sync_queue' table (Section 5.4)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_queue (
            id TEXT PRIMARY KEY,
            capture_id TEXT,
            service TEXT NOT NULL CHECK (service IN ('google','todoist')),
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending','synced','failed')),
            retry_count INTEGER DEFAULT 0,
            last_error TEXT,
            next_retry_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (capture_id) REFERENCES captures(id)
        )
    ''')

    conn.commit()
    conn.close()