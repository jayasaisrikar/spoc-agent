import sqlite3
import json
from typing import Dict
import hashlib


class KnowledgeBase:
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self.init_database()
        self.migrate_database()
    
    def migrate_database(self):
        """Migrate database schema to include file_contents if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if repositories table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repositories'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("Repositories table doesn't exist yet, skipping migration.")
            conn.close()
            return
        
        # Check if file_contents column exists
        cursor.execute("PRAGMA table_info(repositories)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'file_contents' not in columns:
            print("Migrating database schema to include file_contents...")
            cursor.execute('ALTER TABLE repositories ADD COLUMN file_contents TEXT')
            print("Database migration completed.")
        
        if 'file_structure' not in columns:
            print("Migrating database schema to include file_structure...")
            cursor.execute('ALTER TABLE repositories ADD COLUMN file_structure TEXT')
            print("Database migration completed.")
        
        conn.commit()
        conn.close()

    def init_database(self):
        """Initialize SQLite database for knowledge storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                repo_name TEXT UNIQUE,
                repo_hash TEXT,
                file_structure TEXT,
                file_contents TEXT,
                analysis TEXT,
                mermaid_diagram TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY,
                repo_id INTEGER,
                feature_description TEXT,
                suggestions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (repo_id) REFERENCES repositories (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                repo_name TEXT,
                session_id TEXT,
                message_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_repository(self, repo_name: str, repo_data: Dict, analysis: Dict, mermaid: str):
        """Store repository analysis with full file contents in knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        repo_hash = hashlib.md5(
            json.dumps(repo_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Extract file structure (paths only) and file contents separately
        file_structure = list(repo_data.keys())
        file_contents = repo_data
        
        cursor.execute('''
            INSERT OR REPLACE INTO repositories 
            (repo_name, repo_hash, file_structure, file_contents, analysis, mermaid_diagram)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (repo_name, repo_hash, json.dumps(file_structure), 
              json.dumps(file_contents), json.dumps(analysis), mermaid))
        
        conn.commit()
        conn.close()
    
    def get_repository_knowledge(self, repo_name: str) -> Dict:
        """Retrieve full repository knowledge including file contents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_structure, file_contents, analysis, mermaid_diagram 
            FROM repositories 
            WHERE repo_name = ?
        ''', (repo_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'file_structure': json.loads(result[0]),
                'file_contents': json.loads(result[1]),
                'analysis': json.loads(result[2]),
                'mermaid_diagram': result[3]
            }
        return {}
    
    def has_repository(self, repo_name: str) -> bool:
        """Check if repository exists in knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM repositories WHERE repo_name = ?
        ''', (repo_name,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0

    def list_repositories(self):
        """List all repositories in the knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT repo_name, created_at FROM repositories ORDER BY created_at DESC"
        )
        repos = cursor.fetchall()
        conn.close()
        
        return [{"name": repo[0], "analyzed_at": repo[1]} for repo in repos]
    
    def get_all_repositories_knowledge(self) -> Dict:
        """Get knowledge from ALL repositories for cross-repo analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT repo_name, file_structure, file_contents, analysis, mermaid_diagram 
            FROM repositories 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        all_repos = {}
        for result in results:
            repo_name = result[0]
            all_repos[repo_name] = {
                'file_structure': json.loads(result[1]),
                'file_contents': json.loads(result[2]),
                'analysis': json.loads(result[3]),
                'mermaid_diagram': result[4]
            }
        
        return all_repos

    def get_organization_patterns(self) -> Dict:
        """Analyze patterns across all repositories in the organization"""
        all_repos = self.get_all_repositories_knowledge()
        
        patterns = {
            'languages': {},
            'frameworks': {},
            'file_patterns': {},
            'architecture_types': {},
            'common_dependencies': {}
        }
        
        for repo_name, repo_data in all_repos.items():
            analysis = repo_data.get('analysis', {})
            file_structure = repo_data.get('file_structure', [])
            
            # Extract language patterns
            for file_path in file_structure:
                ext = file_path.split('.')[-1] if '.' in file_path else 'no_ext'
                patterns['file_patterns'][ext] = patterns['file_patterns'].get(ext, 0) + 1
            
            # Extract tech stack info from analysis
            tech_stack = analysis.get('tech_stack', {})
            for lang in tech_stack.get('languages', []):
                patterns['languages'][lang] = patterns['languages'].get(lang, 0) + 1
            
            for framework in tech_stack.get('frameworks', []):
                patterns['frameworks'][framework] = patterns['frameworks'].get(framework, 0) + 1
        
        return patterns
    
    def store_chat_message(self, repo_name: str, session_id: str, message_id: str, role: str, content: str, metadata: Dict = None):
        """Store a chat message in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history 
            (repo_name, session_id, message_id, role, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (repo_name, session_id, message_id, role, content, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, repo_name: str, session_id: str = None):
        """Retrieve chat history for a repository"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT message_id, role, content, timestamp, metadata
                FROM chat_history 
                WHERE repo_name = ? AND session_id = ?
                ORDER BY timestamp ASC
            ''', (repo_name, session_id))
        else:
            cursor.execute('''
                SELECT message_id, role, content, timestamp, metadata
                FROM chat_history 
                WHERE repo_name = ?
                ORDER BY timestamp ASC
            ''', (repo_name,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'message_id': row[0],
                'role': row[1],
                'content': row[2],
                'timestamp': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        conn.close()
        return messages
    
    def clear_chat_history(self, repo_name: str, session_id: str = None):
        """Clear chat history for a repository"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('DELETE FROM chat_history WHERE repo_name = ? AND session_id = ?', (repo_name, session_id))
        else:
            cursor.execute('DELETE FROM chat_history WHERE repo_name = ?', (repo_name,))
        
        conn.commit()
        conn.close()
    
    def get_all_chat_sessions(self, repo_name: str = None):
        """Get all chat sessions, optionally filtered by repository"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if repo_name:
            cursor.execute('''
                SELECT DISTINCT repo_name, session_id, MIN(timestamp) as first_message, MAX(timestamp) as last_message, COUNT(*) as message_count
                FROM chat_history 
                WHERE repo_name = ?
                GROUP BY repo_name, session_id
                ORDER BY last_message DESC
            ''', (repo_name,))
        else:
            cursor.execute('''
                SELECT DISTINCT repo_name, session_id, MIN(timestamp) as first_message, MAX(timestamp) as last_message, COUNT(*) as message_count
                FROM chat_history 
                GROUP BY repo_name, session_id
                ORDER BY last_message DESC
            ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'repo_name': row[0],
                'session_id': row[1],
                'first_message': row[2],
                'last_message': row[3],
                'message_count': row[4]
            })
        
        conn.close()
        return sessions
