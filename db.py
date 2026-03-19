import sqlite3
import threading
import os
import json

DB_PATH = os.getenv("DB_PATH", "bot_data.db")
_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    card_index INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_words (
                    user_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, word_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_sentences (
                    user_id INTEGER NOT NULL,
                    sentence_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, sentence_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    user_id INTEGER PRIMARY KEY,
                    current_word_id INTEGER,
                    options_json TEXT,
                    correct_index INTEGER
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sentence_games (
                    user_id INTEGER PRIMARY KEY,
                    sentence_id INTEGER,
                    options_json TEXT,
                    correct_index INTEGER
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


def get_user_index(user_id: int) -> int:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT card_index FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row is None:
                return 0
            return int(row["card_index"])
        finally:
            conn.close()


def set_user_index(user_id: int, index: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (user_id, card_index)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET card_index=excluded.card_index
                """,
                (user_id, index),
            )
            conn.commit()
        finally:
            conn.close()


def add_seen_word(user_id: int, word_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO seen_words (user_id, word_id) VALUES (?, ?)",
                (user_id, word_id),
            )
            conn.commit()
        finally:
            conn.close()


def get_seen_word_ids(user_id: int) -> list:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT word_id FROM seen_words WHERE user_id = ?", (user_id,))
            rows = cur.fetchall()
            return [int(r["word_id"]) for r in rows]
        finally:
            conn.close()


def clear_seen_words(user_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM seen_words WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()


def set_game(user_id: int, current_word_id: int, options: list, correct_index: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO games (user_id, current_word_id, options_json, correct_index)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    current_word_id=excluded.current_word_id,
                    options_json=excluded.options_json,
                    correct_index=excluded.correct_index
                """,
                (user_id, current_word_id, json.dumps(options, ensure_ascii=False), correct_index),
            )
            conn.commit()
        finally:
            conn.close()


def get_game(user_id: int):
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT current_word_id, options_json, correct_index FROM games WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row is None:
                return None
            options = json.loads(row["options_json"]) if row["options_json"] else []
            return {
                "current_word_id": int(row["current_word_id"]) if row["current_word_id"] is not None else None,
                "options": options,
                "correct_index": int(row["correct_index"]) if row["correct_index"] is not None else None,
            }
        finally:
            conn.close()


def clear_game(user_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM games WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()


def add_seen_sentence(user_id: int, sentence_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO seen_sentences (user_id, sentence_id) VALUES (?, ?)",
                (user_id, sentence_id),
            )
            conn.commit()
        finally:
            conn.close()


def get_seen_sentence_ids(user_id: int) -> list:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT sentence_id FROM seen_sentences WHERE user_id = ?", (user_id,))
            rows = cur.fetchall()
            return [int(r["sentence_id"]) for r in rows]
        finally:
            conn.close()


def clear_seen_sentences(user_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM seen_sentences WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()

def set_sentence_game(user_id: int, sentence_id: int, options: list, correct_index: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sentence_games (user_id, sentence_id, options_json, correct_index)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    sentence_id=excluded.sentence_id,
                    options_json=excluded.options_json,
                    correct_index=excluded.correct_index
                """,
                (user_id, sentence_id, json.dumps(options, ensure_ascii=False), correct_index),
            )
            conn.commit()
        finally:
            conn.close()


def get_sentence_game(user_id: int):
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT sentence_id, options_json, correct_index FROM sentence_games WHERE user_id = ?",
                        (user_id,))
            row = cur.fetchone()
            if row is None:
                return None
            options = json.loads(row["options_json"]) if row["options_json"] else []
            return {
                "sentence_id": int(row["sentence_id"]) if row["sentence_id"] is not None else None,
                "options": options,
                "correct_index": int(row["correct_index"]) if row["correct_index"] is not None else None,
            }
        finally:
            conn.close()


def clear_sentence_game(user_id: int) -> None:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM sentence_games WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()


init_db()
