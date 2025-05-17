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

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.execute_sql_file")
    def test_update_user_info(self, mock_execute_sql, mock_get_current_user, client, test_user, token_headers):
        
        mock_get_current_user.return_value = {
            "id": 1,
            "email": test_user["email"]
        }

        
        mock_execute_sql.side_effect = [
            None,  
            [  
                {
                    "id": 1,
                    "user_name": "updated_username",
                    "email": test_user["email"],
                    "is_verified": True,
                    "created_at": "2023-01-01T00:00:00"
                }
            ]
        ]

        update_data = {
            "user_name": "updated_username",
            "first_name": "Updated",
            "occupation": "Data Scientist",
            "has_home": True
        }

        response = client.put(
            "/user/update_info",
            json=update_data,
            headers=token_headers
        )

        assert response.status_code == status.HTTP_200_OK
        updated_user = response.json()
        assert updated_user["user_name"] == "updated_username"
        assert updated_user["email"] == test_user["email"]

        
        mock_execute_sql.assert_called()

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.execute_sql_file")
    def test_update_user_minimal_info(self, mock_execute_sql, mock_get_current_user, client, test_user, token_headers):
        
        mock_get_current_user.return_value = {
            "id": 1,
            "email": test_user["email"]
        }

        
        mock_execute_sql.side_effect = [
            None,  
            [  
                {
                    "id": 1,
                    "user_name": test_user["user_name"],
                    "email": test_user["email"],
                    "is_verified": True,
                    "created_at": "2023-01-01T00:00:00"
                }
            ]
        ]

        
        update_data = {
            "has_medical_conditions": True
        }

        response = client.put(
            "/user/update_info",
            json=update_data,
            headers=token_headers
        )

        assert response.status_code == status.HTTP_200_OK

        
        mock_execute_sql.assert_called()
