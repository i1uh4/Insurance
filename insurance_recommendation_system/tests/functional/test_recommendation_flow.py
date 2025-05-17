import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
import httpx


@pytest.mark.functional
class TestRecommendationFlow:

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_success(self, mock_post, client, recommendation_request, mock_insurance_data):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_insurance_data
        mock_response.raise_for_status = AsyncMock()
        mock_post.return_value = mock_response

        response = client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == status.HTTP_200_OK
        recommendations = response.json()
        assert len(recommendations) == 1
        assert recommendations[0]["product_id"] == mock_insurance_data[0]["product_id"]
        assert recommendations[0]["match_score"] == mock_insurance_data[0]["match_score"]

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_api_error(self, mock_post, client, recommendation_request):
        mock_response = AsyncMock()
        mock_response.status_code = 502
        mock_response.raise_for_status = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=AsyncMock(), response=mock_response
        )
        mock_post.return_value = mock_response

        response = client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert "Error communicating with recommendation system" in response.json()["detail"]

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_exception(self, mock_post, client, recommendation_request):
        mock_post.side_effect = Exception("Connection error")

        response = client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error: Connection error" in response.json()["detail"]

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
