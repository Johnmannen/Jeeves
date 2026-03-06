import os
import logging
import sqlite3
from typing import Optional, List, Dict, Any
from src.agents.exceptions import MemoryDBError

# Konfigurera loggning
logger = logging.getLogger(__name__)

try:
    import libsql_client
except ImportError:
    libsql_client = None

class StateManager:
    """
    Hanterar persistens av dagsform (state) och minnen.
    Designad för att vara 'Cloud Ready' genom att sömlöst växla mellan 
    lokal SQLite och Turso Moln-databas (libSQL) via miljövariabler.
    """
    def __init__(self):
        # Hämtar Turso moln-nycklar
        self.db_url = os.getenv("TURSO_DATABASE_URL")
        self.auth_token = os.getenv("TURSO_AUTH_TOKEN")
        
        self.is_cloud = bool(self.db_url and self.auth_token)
        self.client = None
        
        if self.is_cloud:
            if libsql_client is None:
                logger.warning("[StateManager] Turso-miljö hittad, men libsql-client saknas!")
                logger.warning("[StateManager] Fäller tillbaka till lokal SQLite (ephemeral).")
                self.is_cloud = False
            else:
                try:
                    logger.info(f"[StateManager] Ansluter till Turso Cloud Database: {self.db_url}")
                    self.client = libsql_client.create_client_sync(url=self.db_url, auth_token=self.auth_token)
                except Exception as e:
                    logger.error(f"[StateManager] Kunde inte ansluta till Turso: {e}. Fäller tillbaka.")
                    self.is_cloud = False
                    self.client = None

        if not self.is_cloud:
            self.local_path = os.path.join(os.path.dirname(__file__), '..', '..', 'jeeves_memory.db')
            if os.getenv("VERCEL"):
                # OBS: /tmp/ raderas vid serverless-skalning, varför Turso föredras
                self.local_path = "/tmp/jeeves_memory.db"
            logger.info(f"[StateManager] Använder lokal SQLite: {self.local_path}")
            
        self.init_db()

    def _execute(self, query: str, parameters: tuple = ()):
        """Unified executor för att köra sql-frågor mot antingen Cloud eller Lokal DB."""
        if self.is_cloud and self.client:
            return self.client.execute(query, parameters)
        else:
            with sqlite3.connect(self.local_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                conn.commit()
                return cursor.fetchall()

    def init_db(self):
        """Initierar schema i databasen."""
        try:
            # Användarstate (Stress, Energi)
            self._execute('''
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id TEXT PRIMARY KEY,
                    stress_level INTEGER DEFAULT 5,
                    energy_level INTEGER DEFAULT 5,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Minnen / Brain Dumps
            self._execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    content TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES user_state(user_id)
                )
            ''')
            logger.info("[StateManager] Databas-schema redo.")
        except Exception as e:
            logger.error(f"[StateManager] Initieringsfel: {e}")

    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        """Hämtar fullt state för en användare."""
        try:
            if self.is_cloud and self.client:
                result = self.client.execute('SELECT stress_level, energy_level FROM user_state WHERE user_id = ?', (user_id,))
                if result.rows:
                    row = result.rows[0]
                    return {"stress_level": row[0], "energy_level": row[1]}
            else:
                with sqlite3.connect(self.local_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT stress_level, energy_level FROM user_state WHERE user_id = ?', (user_id,))
                    row = cursor.fetchone()
                    if row:
                        return {"stress_level": row[0], "energy_level": row[1]}
                        
            return {"stress_level": 5, "energy_level": 5}
        except Exception as e:
            logger.warning(f"[StateManager] Kunde inte läsa state för {user_id}: {e}")
            return {"stress_level": 5, "energy_level": 5}

    def update_stress(self, user_id: str, level: int) -> bool:
        """Uppdaterar enbart stressnivån."""
        clamped_level = max(0, min(10, level))
        try:
            self._execute('''
                INSERT INTO user_state (user_id, stress_level) 
                VALUES (?, ?) 
                ON CONFLICT(user_id) DO UPDATE SET 
                    stress_level = excluded.stress_level,
                    last_sync = CURRENT_TIMESTAMP
            ''', (user_id, clamped_level))
            return True
        except Exception as e:
            logger.error(f"[StateManager] Kunde inte uppdatera stress för {user_id}: {e}")
            return False

    def save_memory(self, user_id: str, content: str, category: str = 'insight') -> bool:
        """Sparar ett nytt minne i databasen."""
        try:
            self._execute('''
                INSERT INTO memories (user_id, content, category) 
                VALUES (?, ?, ?)
            ''', (user_id, content, category))
            return True
        except Exception as e:
            logger.error(f"[StateManager] Kunde inte spara minne: {e}")
            return False

# Singleton instance
state_manager = StateManager()

# Bakåtkompatibla funktioner för gamla anrop
def get_stress_level(user_id: str) -> int:
    return state_manager.get_user_state(user_id)["stress_level"]

def update_stress_level(user_id: str, level: int) -> bool:
    return state_manager.update_stress(user_id, level)

def init_db():
    state_manager.init_db()
