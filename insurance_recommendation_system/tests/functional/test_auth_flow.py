import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from jose import jwt
import json


@pytest.mark.functional
class TestAuthFlow:

    @patch("app.services.email_service.send_verification_email")
    async def test_user_registration(self, mock_send_email, client, test_user):
        mock_send_email.return_value = True

        response = client.post(
            "/auth/register",
            json={
                "user_name": test_user["user_name"],
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == 0
        assert "User registered successfully" in data["message"]
        mock_send_email.assert_called_once()

    @patch("app.services.email_service.send_verification_email")
    async def test_registration_duplicate_email(self, mock_send_email, client, test_user):
        mock_send_email.return_value = True

        
        client.post(
            "/auth/register",
            json={
                "user_name": test_user["user_name"],
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )

        
        response = client.post(
            "/auth/register",
            json={
                "user_name": "anotheruser",
                "email": test_user["email"],
                "password": "AnotherPass123!"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    @patch("app.routers.auth.verify_token")
    def test_email_verification(self, mock_verify_token, client):
        mock_verify_token.return_value = {"user_id": 1}

        response = client.get("/auth/verify/fake_token")

        assert response.status_code == status.HTTP_200_OK
        assert "Email verified successfully" in response.json()["message"]

    @patch("app.routers.auth.verify_token")
    def test_email_verification_invalid_token(self, mock_verify_token, client):
        mock_verify_token.side_effect = Exception("Invalid token")

        response = client.get("/auth/verify/invalid_token")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid verification token" in response.json()["detail"]

    @patch("app.routers.auth.execute_sql_file")
    @patch("app.routers.auth.verify_password")
    def test_login_successful(self, mock_verify_password, mock_execute_sql, client, test_user):
        
        mock_execute_sql.return_value = [{
            "id": 1,
            "user_name": test_user["user_name"],
            "email": test_user["email"],
            "password": "hashed_password",
            "is_verified": True,
            "created_at": "2023-01-01T00:00:00"
        }]

        
        mock_verify_password.return_value = True

        response = client.post(
            "/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user["email"]

    @patch("app.routers.auth.execute_sql_file")
    def test_login_user_not_found(self, mock_execute_sql, client):
        
        mock_execute_sql.return_value = []

        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123!"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    @patch("app.routers.auth.execute_sql_file")
    def test_login_not_verified(self, mock_execute_sql, client, test_user):
        
        mock_execute_sql.return_value = [{
            "id": 1,
            "user_name": test_user["user_name"],
            "email": test_user["email"],
            "password": "hashed_password",
            "is_verified": False,
            "created_at": "2023-01-01T00:00:00"
        }]

        response = client.post(
            "/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Email not verified" in response.json()["detail"]

    @patch("app.routers.auth.execute_sql_file")
    @patch("app.routers.auth.verify_password")
    def test_login_invalid_credentials(self, mock_verify_password, mock_execute_sql, client, test_user):
        
        mock_execute_sql.return_value = [{
            "id": 1,
            "user_name": test_user["user_name"],
            "email": test_user["email"],
            "password": "hashed_password",
            "is_verified": True,
            "created_at": "2023-01-01T00:00:00"
        }]

        
        mock_verify_password.return_value = False

        response = client.post(
            "/auth/login",
            json={
                "email": test_user["email"],
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials" in response.json()["detail"]
