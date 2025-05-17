import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from app.database import execute_sql_file, get_db, get_slave_db


@pytest.mark.integration
class TestDbIntegration:

    @patch("psycopg2.connect")
    def test_execute_sql_file_read(self, mock_connect, monkeypatch):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "SELECT * FROM test"

        with patch("builtins.open", return_value=mock_file):
            result = execute_sql_file("test.sql", {"param": "value"}, read_only=True)

        assert result == [{"id": 1, "name": "test"}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", {"param": "value"})
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_execute_sql_file_write(self, mock_connect, monkeypatch):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = psycopg2.ProgrammingError("no results")

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "INSERT INTO test VALUES (1)"

        with patch("builtins.open", return_value=mock_file):
            result = execute_sql_file("test.sql", {"param": "value"}, read_only=False)

        assert result is None
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (1)", {"param": "value"})
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_execute_sql_file_error(self, mock_connect, monkeypatch):
        mock_connect.side_effect = psycopg2.OperationalError("connection error")

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "SELECT * FROM test"

        with patch("builtins.open", return_value=mock_file):
            with pytest.raises(psycopg2.OperationalError):
                execute_sql_file("test.sql", {"param": "value"})

    def test_get_db(self):
        db_gen = get_db()

        with patch("app.database.SessionLocal") as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance

            session = next(db_gen)

            with pytest.raises(StopIteration):
                next(db_gen)

            mock_session_instance.close.assert_called_once()

    def test_get_slave_db(self):
        db_gen = get_slave_db()

        with patch("app.database.SlaveSessionLocal") as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance

            session = next(db_gen)

            with pytest.raises(StopIteration):
                next(db_gen)

            mock_session_instance.close.assert_called_once()
