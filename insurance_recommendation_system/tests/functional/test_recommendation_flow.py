import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
import httpx


@pytest.mark.functional
class TestRecommendationFlow:

    @patch("app.routers.recommendations.execute_sql_file")
    def test_check_recommendation(self, mock_execute_sql, client):
        mock_execute_sql.side_effect = [
            [{"id": 1, "email": "test@example.com"}],
            None
        ]

        response = client.post(
            "/recommendation/check_recommendation",
            json={
                "product_id": 1,
                "user_email": "test@example.com"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["code"] == 0
        assert result["message"] == "Success"

        assert mock_execute_sql.call_count == 2

    @patch("app.routers.recommendations.execute_sql_file")
    def test_check_recommendation_user_not_found(self, mock_execute_sql, client):
        mock_execute_sql.return_value = []

        response = client.post(
            "/recommendation/check_recommendation",
            json={
                "product_id": 1,
                "user_email": "nonexistent@example.com"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User with this email not found" in response.json()["detail"]
