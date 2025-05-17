import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.routers.users import get_current_user_info, update_user_info


class TestUserRoutes:
    """Тесты для маршрутов пользователей"""

    @patch('app.routers.users.execute_sql_file')
    def test_get_current_user_info_success(self, mock_execute_sql_file):
        """Тест успешного получения информации о пользователе"""
        
        mock_user_data = [{
            "user_name": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "gender": "male",
            "occupation": "Developer",
            "income": 75000.0,
            "marital_status": "single",
            "has_children": False,
            "has_vehicle": True,
            "has_home": False,
            "has_medical_conditions": False,
            "travel_frequency": "often"
        }]

        mock_execute_sql_file.return_value = mock_user_data

        
        from app.models.user_models import UserInfoRequest
        request = UserInfoRequest(email="test@example.com")

        
        result = get_current_user_info(request)

        
        assert result["email"] == "test@example.com"
        assert result["user_name"] == "testuser"
        assert result["first_name"] == "Test"
        assert result["age"] == 30
        assert result["income"] == 75000.0

        
        mock_execute_sql_file.assert_called_once_with(
            "users/get_user_info.sql",
            {"email": "test@example.com"},
            read_only=True
        )

    @patch('app.routers.users.execute_sql_file')
    def test_get_current_user_info_not_found(self, mock_execute_sql_file):
        """Тест случая, когда пользователь не найден"""
        
        mock_execute_sql_file.return_value = []

        
        from app.models.user_models import UserInfoRequest
        request = UserInfoRequest(email="nonexistent@example.com")

        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_info(request)

        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    @patch('app.routers.users.execute_sql_file')
    def test_update_user_info_success(self, mock_execute_sql_file):
        """Тест успешного обновления информации о пользователе"""
        
        mock_updated_user = [{
            "id": 1,
            "user_name": "updateduser",
            "email": "test@example.com",
            "is_verified": True,
            "created_at": "2023-01-01T00:00:00Z"
        }]

        
        mock_execute_sql_file.side_effect = [None, mock_updated_user]

        
        from app.models.user_models import UserUpdate
        user_data = UserUpdate(
            user_name="updateduser",
            first_name="Updated",
            last_name="User",
            age=35
        )

        
        current_user = {
            "id": 1,
            "email": "test@example.com"
        }

        
        result = update_user_info(user_data, current_user)

        
        assert result["id"] == 1
        assert result["user_name"] == "updateduser"
        assert result["email"] == "test@example.com"
        assert result["is_verified"] is True

        
        
        first_call_args = mock_execute_sql_file.call_args_list[0][0]
        assert first_call_args[0] == "users/update_user_info.sql"

        
        second_call_args = mock_execute_sql_file.call_args_list[1][0]
        assert second_call_args[0] == "users/get_user_by_id.sql"
        assert second_call_args[1] == {"id": 1}