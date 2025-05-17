import pytest
from unittest.mock import patch, MagicMock
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_user
from fastapi import HTTPException
from jose import jwt
import os
from datetime import datetime, timedelta


class TestAuthUtils:
    """Тесты для утилит аутентификации"""

    def test_password_hash_verify(self):
        """Проверка хеширования и верификации пароля"""
        password = "testPassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongPassword", hashed) is False

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_create_access_token(self):
        """Проверка создания JWT токена"""
        user_data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(user_data)
        assert isinstance(token, str)
        payload = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    @patch('app.utils.auth.jwt.decode')
    @patch('app.utils.auth.execute_sql_file')
    def test_get_current_user_success(self, mock_execute_sql_file, mock_jwt_decode):
        """Проверка получения текущего пользователя из токена"""
        mock_jwt_decode.return_value = {"user_id": 1}

        mock_user = [{"id": 1, "email": "test@example.com", "user_name": "testuser"}]
        mock_execute_sql_file.return_value = mock_user

        user = get_current_user("fake_token")

        assert user == mock_user[0]
        mock_execute_sql_file.assert_called_once_with("users/get_user_by_id.sql", {"id": 1})

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_invalid_token(self, mock_jwt_decode):
        """Проверка обработки невалидного токена"""
        mock_jwt_decode.side_effect = jwt.JWTError("Invalid token")

        with pytest.raises(HTTPException) as excinfo:
            get_current_user("invalid_token")

        assert excinfo.value.status_code == 401

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_missing_user_id(self, mock_jwt_decode):
        """Проверка обработки токена без user_id"""
        mock_jwt_decode.return_value = {"email": "test@example.com"}

        with pytest.raises(HTTPException) as excinfo:
            get_current_user("incomplete_token")

        assert excinfo.value.status_code == 401

    @patch('app.utils.auth.jwt.decode')
    @patch('app.utils.auth.execute_sql_file')
    def test_get_current_user_user_not_found(self, mock_execute_sql_file, mock_jwt_decode):
        """Проверка обработки случая, когда пользователь не найден в базе"""
        mock_jwt_decode.return_value = {"user_id": 999}

        mock_execute_sql_file.return_value = []

        with pytest.raises(HTTPException) as excinfo:
            get_current_user("user_not_found_token")

        assert excinfo.value.status_code == 401
