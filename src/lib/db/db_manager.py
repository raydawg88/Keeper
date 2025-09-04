"""
Database Manager for Keeper
Handles connections and operations with Supabase PostgreSQL
"""

import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any


class DatabaseManager:
    """Manages database connections and operations for Keeper"""
    
    def __init__(self):
        self.connection_string = self._build_connection_string()
        self._connection = None
    
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string from Supabase credentials"""
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        
        # Parse Supabase URL to get database connection details
        # Supabase URLs are like: https://project.supabase.co
        # Database connection is: postgresql://postgres:[password]@db.project.supabase.co:5432/postgres
        
        parsed = urlparse(supabase_url)
        project_id = parsed.hostname.split('.')[0]
        
        # Build PostgreSQL connection string
        db_host = f"db.{project_id}.supabase.co"
        db_user = "postgres"
        db_password = service_key  # Use the full JWT service key as password
        db_name = "postgres"
        db_port = 5432
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    def get_connection(self):
        """Get database connection, creating if needed"""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    self.connection_string,
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
                self._connection.autocommit = True
            except Exception as e:
                print(f"Database connection error: {e}")
                raise
        
        return self._connection
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> bool:
        """Execute SQL statement"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return True
        except Exception as e:
            print(f"SQL execution error: {e}")
            return False
    
    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch single row as dictionary"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"Fetch one error: {e}")
            return None
    
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetch all rows as list of dictionaries"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Fetch all error: {e}")
            return []
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a record into specified table"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())
            
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            return self.execute_sql(sql, values)
        except Exception as e:
            print(f"Insert error: {e}")
            return False
    
    def update_record(self, table: str, data: Dict[str, Any], where_clause: str, where_params: tuple) -> bool:
        """Update records in specified table"""
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            values = tuple(data.values()) + where_params
            
            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            return self.execute_sql(sql, values)
        except Exception as e:
            print(f"Update error: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        result = self.fetch_one(sql, (table_name,))
        return result['exists'] if result else False
    
    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None


# Global database manager instance
db = DatabaseManager()