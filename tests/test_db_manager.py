# tests/test_db_manager.py

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from components import db_manager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_conversations.db"
        with patch('config.LOGGING_ENABLED', True), \
             patch('config.LOGGING_DB_PATH', str(db_path)):
            yield db_path


@pytest.fixture
def disabled_logging():
    """Mock logging as disabled."""
    with patch('config.LOGGING_ENABLED', False):
        yield


class TestDatabaseManager:
    """Test cases for db_manager component."""

    def test_save_and_retrieve_conversation(self, temp_db):
        """Test saving and retrieving a conversation."""
        # Save a conversation
        db_manager.save_conversation(
            user_input="Hello, how are you?",
            assistant_response="I'm doing great, thanks!",
            status="completed"
        )

        # Retrieve conversations
        conversations = db_manager.get_conversations(limit=10)

        assert len(conversations) == 1
        assert conversations[0]['user_input'] == "Hello, how are you?"
        assert conversations[0]['assistant_response'] == "I'm doing great, thanks!"
        assert conversations[0]['status'] == "completed"
        assert conversations[0]['error_message'] is None

    def test_search_by_keyword(self, temp_db):
        """Test searching conversations by keyword."""
        # Save multiple conversations
        db_manager.save_conversation("What's the weather?", "I can't check weather.", "completed")
        db_manager.save_conversation("Tell me a joke", "Why did the chicken cross the road?", "completed")
        db_manager.save_conversation("What's the weather like today?", "Still can't check weather.", "completed")

        # Search for "weather"
        results = db_manager.get_conversations(limit=10, search="weather")

        assert len(results) == 2
        assert all("weather" in r['user_input'].lower() or "weather" in (r['assistant_response'] or "").lower() for r in results)

    def test_filter_by_date(self, temp_db):
        """Test filtering conversations by date."""
        # Save a conversation
        db_manager.save_conversation("Hello", "Hi there", "completed")

        # Get today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Filter by today's date
        results = db_manager.get_conversations(limit=10, start_date=today)

        assert len(results) >= 1

        # Filter by future date (should return nothing)
        results = db_manager.get_conversations(limit=10, start_date="2999-12-31")

        assert len(results) == 0

    def test_database_auto_creation(self, temp_db):
        """Test that database file and directory are auto-created."""
        # Ensure database doesn't exist yet
        assert not temp_db.exists()

        # Save a conversation (should create database)
        db_manager.save_conversation("Test", "Response", "completed")

        # Verify database file was created
        assert temp_db.exists()

        # Verify table schema exists
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
        tables = cursor.fetchall()
        conn.close()

        assert len(tables) == 1
        assert tables[0][0] == 'conversations'

    def test_failed_conversation_logging(self, temp_db):
        """Test logging failed conversations with error messages."""
        # Save a failed conversation
        db_manager.save_conversation(
            user_input="What's 2+2?",
            assistant_response=None,
            status="failed",
            error="LLM timeout error"
        )

        # Retrieve the failed conversation
        conversations = db_manager.get_conversations(limit=10)

        assert len(conversations) == 1
        assert conversations[0]['status'] == "failed"
        assert conversations[0]['assistant_response'] is None
        assert conversations[0]['error_message'] == "LLM timeout error"

    def test_disabled_mode(self, disabled_logging):
        """Test that operations are no-ops when logging is disabled."""
        # These should all be no-ops (not create any files or raise errors)
        db_manager.save_conversation("Test", "Response", "completed")

        results = db_manager.get_conversations(limit=10)

        # Should return empty list
        assert results == []

    def test_limit_parameter(self, temp_db):
        """Test that limit parameter correctly limits results."""
        # Save 15 conversations
        for i in range(15):
            db_manager.save_conversation(f"User message {i}", f"Assistant response {i}", "completed")

        # Request only 5
        results = db_manager.get_conversations(limit=5)

        assert len(results) == 5

        # Request all
        results = db_manager.get_conversations(limit=100)

        assert len(results) == 15

    def test_invalid_date_format(self, temp_db):
        """Test that invalid date format is handled gracefully."""
        # Save a conversation
        db_manager.save_conversation("Test", "Response", "completed")

        # Query with invalid date (should be ignored and show all results)
        results = db_manager.get_conversations(limit=10, start_date="not-a-date")

        # Should still return the conversation (date filter ignored)
        assert len(results) == 1

    def test_wal_mode_enabled(self, temp_db):
        """Test that WAL mode is enabled for concurrent access."""
        # Save a conversation to initialize database
        db_manager.save_conversation("Test", "Response", "completed")

        # Check journal mode
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()

        assert mode.upper() == "WAL"
