import sqlite3
import threading
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        try:
            with self.lock:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )''')
                    
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        raw_transcript TEXT NOT NULL,
                        formatted_text TEXT NOT NULL,
                        language TEXT DEFAULT 'en',
                        app_context TEXT DEFAULT 'general',
                        window_title TEXT DEFAULT '',
                        duration_seconds REAL DEFAULT 0.0,
                        word_count INTEGER DEFAULT 0,
                        was_gibberish INTEGER DEFAULT 0,
                        speaker_verified INTEGER DEFAULT 1
                    )''')
                    
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dictionary (
                        word TEXT PRIMARY KEY,
                        added_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
                    
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS snippets (
                        trigger_phrase TEXT PRIMARY KEY,
                        expansion TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        added_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
                    
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_profiles (
                        app_pattern TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        tone TEXT DEFAULT 'general',
                        custom_prompt TEXT DEFAULT '',
                        enabled INTEGER DEFAULT 1
                    )''')
                    conn.commit()
        except sqlite3.DatabaseError as e:
            logger.error(f"Database corruption or initialization error: {e}")
            raise

    # --- Settings ---
    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default

    def set_setting(self, key, value):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
                conn.commit()

    def get_all_settings(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {row['key']: row['value'] for row in cursor.fetchall()}

    def delete_setting(self, key):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM settings WHERE key=?", (key,))
                conn.commit()

    # --- History ---
    def add_history(self, raw, formatted, language, app_context, window_title, duration, word_count, was_gibberish=0, speaker_verified=1):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO history (raw_transcript, formatted_text, language, app_context, window_title, duration_seconds, word_count, was_gibberish, speaker_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (raw, formatted, language, app_context, window_title, duration, word_count, was_gibberish, speaker_verified))
                conn.commit()
                return cursor.lastrowid

    def get_history(self, limit=50, offset=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def search_history(self, query):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_query = f"%{query}%"
            cursor.execute("SELECT * FROM history WHERE raw_transcript LIKE ? OR formatted_text LIKE ? ORDER BY timestamp DESC", (search_query, search_query))
            return [dict(row) for row in cursor.fetchall()]

    def delete_history(self, history_id):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history WHERE id=?", (history_id,))
                conn.commit()

    def get_history_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM history")
            return cursor.fetchone()[0]

    def clear_history(self):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()

    # --- Dictionary ---
    def add_word(self, word):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO dictionary (word) VALUES (?)", (word,))
                conn.commit()
                return cursor.rowcount > 0

    def remove_word(self, word):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dictionary WHERE word=?", (word,))
                conn.commit()
                return cursor.rowcount > 0

    def get_all_words(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dictionary ORDER BY added_date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def word_exists(self, word):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM dictionary WHERE word=?", (word,))
            return cursor.fetchone() is not None

    # --- Snippets ---
    def add_snippet(self, trigger, expansion):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO snippets (trigger_phrase, expansion) VALUES (?, ?)", (trigger, expansion))
                conn.commit()

    def remove_snippet(self, trigger):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM snippets WHERE trigger_phrase=?", (trigger,))
                conn.commit()

    def get_all_snippets(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM snippets ORDER BY added_date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def increment_snippet_usage(self, trigger):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE snippets SET usage_count = usage_count + 1 WHERE trigger_phrase=?", (trigger,))
                conn.commit()

    # --- Profiles ---
    def add_profile(self, app_pattern, display_name, tone='general', custom_prompt='', enabled=1):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT OR REPLACE INTO app_profiles (app_pattern, display_name, tone, custom_prompt, enabled)
                VALUES (?, ?, ?, ?, ?)
                ''', (app_pattern, display_name, tone, custom_prompt, enabled))
                conn.commit()

    def remove_profile(self, app_pattern):
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM app_profiles WHERE app_pattern=?", (app_pattern,))
                conn.commit()

    def get_all_profiles(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM app_profiles")
            return [dict(row) for row in cursor.fetchall()]

    def get_profile_for_app(self, window_title):
        if not window_title:
            return None
        profiles = self.get_all_profiles()
        window_title_lower = window_title.lower()
        for profile in profiles:
            if profile['enabled'] and profile['app_pattern'].lower() in window_title_lower:
                return profile
        return None

    # --- Stats ---
    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(word_count), COUNT(*), SUM(duration_seconds), COUNT(DISTINCT language), COUNT(DISTINCT app_context) FROM history WHERE was_gibberish=0")
            row = cursor.fetchone()
            total_words = row[0] or 0
            total_dictations = row[1] or 0
            total_duration = row[2] or 0.0
            unique_languages = row[3] or 0
            unique_apps = row[4] or 0
            
            avg_words = total_words / total_dictations if total_dictations > 0 else 0
            
            cursor.execute("SELECT SUM(word_count), COUNT(*) FROM history WHERE date(timestamp) = date('now', 'localtime') AND was_gibberish=0")
            today_row = cursor.fetchone()
            words_today = today_row[0] or 0
            dictations_today = today_row[1] or 0
            
            return {
                "total_words": total_words,
                "total_dictations": total_dictations,
                "total_duration": total_duration,
                "unique_languages": unique_languages,
                "unique_apps": unique_apps,
                "avg_words_per_dictation": round(avg_words, 2),
                "words_today": words_today,
                "dictations_today": dictations_today
            }
