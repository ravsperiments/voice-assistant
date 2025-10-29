# components/db_manager.py

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import config


def _ensure_db_directory() -> None:
    """Ensure the database directory exists."""
    if not config.LOGGING_ENABLED:
        return

    db_path = Path(config.LOGGING_DB_PATH)
    db_dir = db_path.parent

    if not db_dir.exists():
        try:
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Failed to create database directory {db_dir}: {e}")


def _get_connection() -> Optional[sqlite3.Connection]:
    """
    Get a database connection with WAL mode enabled.
    Returns None if logging is disabled.
    """
    if not config.LOGGING_ENABLED:
        return None

    try:
        _ensure_db_directory()
        conn = sqlite3.Connection(config.LOGGING_DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    except Exception as e:
        print(f"Warning: Failed to connect to database: {e}")
        return None


def _initialize_schema(conn: sqlite3.Connection) -> None:
    """Create the conversations table if it doesn't exist."""
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                assistant_response TEXT,
                status TEXT DEFAULT 'completed',
                error_message TEXT,
                schema_version INTEGER DEFAULT 1
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON conversations(created_at)")
        conn.commit()
    except Exception as e:
        print(f"Warning: Failed to initialize database schema: {e}")


def save_conversation(
    user_input: str,
    assistant_response: Optional[str] = None,
    status: str = 'completed',
    error: Optional[str] = None
) -> None:
    """
    Save a conversation turn to the database.

    Args:
        user_input: The user's input text
        assistant_response: The assistant's response text (None if failed)
        status: 'completed' or 'failed'
        error: Error message if status is 'failed'
    """
    if not config.LOGGING_ENABLED:
        return

    conn = _get_connection()
    if conn is None:
        return

    try:
        _initialize_schema(conn)
        conn.execute(
            """
            INSERT INTO conversations (user_input, assistant_response, status, error_message)
            VALUES (?, ?, ?, ?)
            """,
            (user_input, assistant_response, status, error)
        )
        conn.commit()
    except Exception as e:
        print(f"Warning: Failed to save conversation: {e}")
    finally:
        if conn:
            conn.close()


def get_conversations(
    limit: int = 10,
    search: Optional[str] = None,
    start_date: Optional[str] = None
) -> List[Dict]:
    """
    Query conversations with optional filters.

    Args:
        limit: Maximum number of conversations to return
        search: Optional keyword to search in user_input or assistant_response
        start_date: Optional date string (YYYY-MM-DD) to filter conversations after this date

    Returns:
        List of conversation dictionaries, ordered by created_at DESC
    """
    if not config.LOGGING_ENABLED:
        return []

    conn = _get_connection()
    if conn is None:
        return []

    try:
        _initialize_schema(conn)

        query = "SELECT * FROM conversations WHERE 1=1"
        params = []

        if search:
            query += " AND (user_input LIKE ? OR assistant_response LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        if start_date:
            # Validate date format
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                query += " AND DATE(created_at) >= ?"
                params.append(start_date)
            except ValueError:
                print(f"Warning: Invalid date format '{start_date}', expected YYYY-MM-DD")

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        # Convert Row objects to dictionaries
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'created_at': row['created_at'],
                'user_input': row['user_input'],
                'assistant_response': row['assistant_response'],
                'status': row['status'],
                'error_message': row['error_message'],
                'schema_version': row['schema_version']
            })

        return results
    except Exception as e:
        print(f"Warning: Failed to query conversations: {e}")
        return []
    finally:
        if conn:
            conn.close()
