import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


@pytest.mark.functional
class TestUserFlow:

    @patch("app.routers.users.execute_sql_file")
    def test_get_user_info_success(self, mock_execute_sql, client, test_user):
        mock_execute_sql.return_value = [
            {
                "user_name": test_user["user_name"],
                "email": test_user["email"],
                "first_name": test_user["first_name"],
                "last_name": test_user["last_name"],
                "age": test_user["age"],
                "gender": test_user["gender"],
                "occupation": test_user["occupation"],
                "income": test_user["income"],
                "marital_status": test_user["marital_status"],
                "has_children": test_user["has_children"],
                "has_vehicle": test_user["has_vehicle"],
                "has_home": test_user["has_home"],
                "has_medical_conditions": test_user["has_medical_conditions"],
                "travel_frequency": test_user["travel_frequency"]
            }
        ]

        response = client.post(
            "/user/info",
            json={"email": test_user["email"]}
        )

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["email"] == test_user["email"]
        assert user_data["age"] == test_user["age"]
        assert user_data["gender"] == test_user["gender"]
        assert user_data["occupation"] == test_user["occupation"]

    @patch("app.routers.users.execute_sql_file")
    def test_get_user_info_not_found(self, mock_execute_sql, client):
        mock_execute_sql.return_value = []

        response = client.post(
            "/user/info",
            json={"email": "nonexistent@example.com"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
