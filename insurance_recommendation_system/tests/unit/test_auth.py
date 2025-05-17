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

        # Проверяем, что хеш не совпадает с оригинальным паролем
        assert hashed != password

        # Проверяем, что верификация проходит успешно
        assert verify_password(password, hashed) is True

        # Проверяем, что неверный пароль не проходит верификацию
        assert verify_password("wrongPassword", hashed) is False

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_create_access_token(self):
        """Проверка создания JWT токена"""
        user_data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(user_data)

        # Проверяем, что токен создан и является строкой
        assert isinstance(token, str)

        # Декодируем токен и проверяем данные
        payload = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        # Проверяем, что токен имеет срок действия
        assert "exp" in payload

    @patch('app.utils.auth.jwt.decode')
    @patch('app.utils.auth.execute_sql_file')
    def test_get_current_user_success(self, mock_execute_sql_file, mock_jwt_decode):
        """Проверка получения текущего пользователя из токена"""
        # Настраиваем мок для jwt.decode
        mock_jwt_decode.return_value = {"user_id": 1}

        # Настраиваем мок для execute_sql_file
        mock_user = [{"id": 1, "email": "test@example.com", "user_name": "testuser"}]
        mock_execute_sql_file.return_value = mock_user

        # Вызываем функцию
        user = get_current_user("fake_token")

        # Проверяем результат
        assert user == mock_user[0]
        mock_execute_sql_file.assert_called_once_with("users/get_user_by_id.sql", {"id": 1})

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_invalid_token(self, mock_jwt_decode):
        """Проверка обработки невалидного токена"""
        # Настраиваем мок для jwt.decode, чтобы он вызывал исключение
        mock_jwt_decode.side_effect = jwt.JWTError("Invalid token")

        # Проверяем, что функция вызывает исключение HTTPException
        with pytest.raises(HTTPException) as excinfo:
            get_current_user("invalid_token")

        # Проверяем статус-код исключения
        assert excinfo.value.status_code == 401

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_missing_user_id(self, mock_jwt_decode):
        """Проверка обработки токена без user_id"""
        # Настраиваем мок для jwt.decode
        mock_jwt_decode.return_value = {"email": "test@example.com"}  # Нет user_id

        # Проверяем, что функция вызывает исключение HTTPException
        with pytest.raises(HTTPException) as excinfo:
            get_current_user("incomplete_token")

        # Проверяем статус-код исключения
        assert excinfo.value.status_code == 401

    @patch('app.utils.auth.jwt.decode')
    @patch('app.utils.auth.execute_sql_file')
    def test_get_current_user_user_not_found(self, mock_execute_sql_file, mock_jwt_decode):
        """Проверка обработки случая, когда пользователь не найден в базе"""
        # Настраиваем мок для jwt.decode
        mock_jwt_decode.return_value = {"user_id": 999}  # Несуществующий ID

        # Настраиваем мок для execute_sql_file - пользователь не найден
        mock_execute_sql_file.return_value = []

        # Проверяем, что функция вызывает исключение HTTPException
        with pytest.raises(HTTPException) as excinfo:
            get_current_user("user_not_found_token")

        # Проверяем статус-код исключения
        assert excinfo.value.status_code == 401
