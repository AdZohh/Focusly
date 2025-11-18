# src/data/database.py
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "focusly.db"))

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    """Inicializar base de datos con tablas para sesiones"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla sessions existe y tiene las columnas correctas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Verificar si tiene las columnas nuevas
            cursor.execute("PRAGMA table_info(sessions)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'duration_seconds' not in columns:
                print("[DB] Actualizando esquema de base de datos...")
                # Backup de datos existentes si los hay
                cursor.execute("ALTER TABLE sessions RENAME TO sessions_old")
        
        # Crear tablas nuevas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                final_score INTEGER NOT NULL,
                apps_used TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                app_name TEXT NOT NULL,
                app_title TEXT NOT NULL,
                total_seconds INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Si había tabla old, migrar datos (opcional)
        # ...
        
        conn.commit()
        print("[DB] Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"[DB] Error inicializando base de datos: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_session(start_time, end_time, duration_seconds, final_score, apps_used):
    """Guardar una sesión completada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (start_time, end_time, duration_seconds, final_score, apps_used)
        VALUES (?, ?, ?, ?, ?)
    ''', (start_time, end_time, duration_seconds, final_score, apps_used))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_session_apps(session_id, app_data):
    """Guardar datos de apps usadas en una sesión"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for app_name, app_title, total_seconds in app_data:
        cursor.execute('''
            INSERT INTO session_apps (session_id, app_name, app_title, total_seconds)
            VALUES (?, ?, ?, ?)
        ''', (session_id, app_name, app_title, total_seconds))
    
    conn.commit()
    conn.close()

def get_all_sessions():
    """Obtener todas las sesiones ordenadas por fecha"""
    print("🔍 [DATABASE] get_all_sessions llamado")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Primero verificar qué tablas existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 [DATABASE] Tablas existentes: {[table[0] for table in tables]}")
        
        # Verificar estructura de la tabla sessions
        if 'sessions' in [table[0] for table in tables]:
            cursor.execute("PRAGMA table_info(sessions)")
            columns = cursor.fetchall()
            print(f"📋 [DATABASE] Columnas de 'sessions': {[col[1] for col in columns]}")
        
        cursor.execute('''
            SELECT id, start_time, end_time, duration_seconds, final_score, apps_used
            FROM sessions 
            ORDER BY start_time DESC
        ''')
        
        sessions = cursor.fetchall()
        print(f"✅ [DATABASE] Sesiones obtenidas: {len(sessions)}")
        
        return sessions
        
    except Exception as e:
        print(f"❌ [DATABASE] Error en get_all_sessions: {e}")
        return []
    finally:
        conn.close()

def get_session_apps(session_id):
    """Obtener apps usadas en una sesión específica"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT app_name, app_title, total_seconds
        FROM session_apps
        WHERE session_id = ?
        ORDER BY total_seconds DESC
    ''', (session_id,))
    
    apps = cursor.fetchall()
    conn.close()
    return apps
