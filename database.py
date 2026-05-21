import sqlite3
from models import MAP

class DatabaseManager:
    """
    SQLite database manager - MAPs ko persist karta hai
    """
    
    def __init__(self, db_path="regulatory_ai.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Database connection lo"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Tables banao agar exist nahi karte"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER,
                    action TEXT NOT NULL,
                    department TEXT NOT NULL,
                    deadline TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'Pending',
                    compliance_risk TEXT,
                    estimated_effort TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    session_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    map_id INTEGER,
                    old_status TEXT,
                    new_status TEXT,
                    changed_at TEXT,
                    session_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    message TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()
    
    def save_maps(self, maps_list, session_id):
        """MAPs database mein save karo"""
        with self.get_connection() as conn:
            # Pehle session ke purane MAPs delete karo
            conn.execute("DELETE FROM maps WHERE session_id = ?", (session_id,))
            
            # Naye MAPs insert karo
            for m in maps_list:
                conn.execute("""
                    INSERT INTO maps VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    m['id'], m['action'], m['department'],
                    m['deadline'], m['priority'], m['status'],
                    m.get('compliance_risk', ''),
                    m.get('estimated_effort', 'Medium'),
                    m.get('created_at', ''), m.get('updated_at', ''),
                    session_id
                ))
            conn.commit()
    
    def load_maps(self, session_id):
        """Database se MAPs lo"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM maps WHERE session_id = ?", 
                (session_id,)
            )
            rows = cursor.fetchall()
            
            maps = []
            for row in rows:
                maps.append({
                    'id': row[0], 'action': row[1],
                    'department': row[2], 'deadline': row[3],
                    'priority': row[4], 'status': row[5],
                    'compliance_risk': row[6],
                    'estimated_effort': row[7]
                })
            return maps
    
    def update_map_status(self, map_id, new_status, old_status, session_id):
        """Status update karo aur audit log mein save karo"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.get_connection() as conn:
            # Status update
            conn.execute("""
                UPDATE maps SET status = ?, updated_at = ?
                WHERE id = ? AND session_id = ?
            """, (new_status, now, map_id, session_id))
            
            # Audit log entry
            conn.execute("""
                INSERT INTO audit_log 
                (map_id, old_status, new_status, changed_at, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (map_id, old_status, new_status, now, session_id))
            
            conn.commit()
    
    def save_chat_message(self, session_id, role, message):
        """Chat history save karo"""
        from datetime import datetime
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO chat_history (session_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, message, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
    
    def load_chat_history(self, session_id):
        """Chat history load karo"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT role, message FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            return [{'role': r[0], 'content': r[1]} 
                    for r in cursor.fetchall()]
    
    def get_audit_log(self, session_id):
        """Audit log load karo"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT map_id, old_status, new_status, changed_at 
                FROM audit_log
                WHERE session_id = ?
                ORDER BY changed_at DESC
                LIMIT 10
            """, (session_id,))
            return [{
                'map_id': r[0], 'old_status': r[1],
                'new_status': r[2], 'timestamp': r[3]
            } for r in cursor.fetchall()]