from locust import HttpUser, task, between
from app.models.user_models import UserCreate, UserLogin
from app.models.recommendation_models import InsuranceRecommendationRequest
import random
import json
import logging


class AuthenticationUser(HttpUser):
    """
    Locust user class for testing authentication endpoints
    """
    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user with random credentials"""
        self.user_id = random.randint(10000, 99999)
        self.username = f"loadtest_user_{self.user_id}"
        self.email = f"loadtest_{self.user_id}@example.com"
        self.password = "LoadTest123!"
        self.token = None

    @task(1)
    def register_user(self):
        """Task to register a new user"""
        user_data = {
            "user_name": self.username,
            "email": self.email,
            "password": self.password
        }

        with self.client.post("/auth/register", json=user_data, catch_response=True) as response:
            if response.status_code == 200:
                logging.info(f"Successfully registered user: {self.email}")
            elif response.status_code == 400 and "already exists" in response.text:

                response.success()
                logging.info(f"User already exists: {self.email}")
            else:
                logging.error(f"Failed to register user: {response.status_code}, {response.text}")
                response.failure(f"Registration failed with status code: {response.status_code}")

    @task(3)
    def login_user(self):
        """Task to login a user"""
        login_data = {
            "email": self.email,
            "password": self.password
        }

        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                logging.info(f"Successfully logged in user: {self.email}")
            elif response.status_code == 403 and "not verified" in response.text.lower():

                response.success()
                logging.info(f"User not verified: {self.email}")
            elif response.status_code == 404 or response.status_code == 401:

                self.register_user()
                response.success()
            else:
                logging.error(f"Failed to login: {response.status_code}, {response.text}")
                response.failure(f"Login failed with status code: {response.status_code}")

    @task(1)
    def verify_email_simulation(self):
        """
        Simulates email verification
        Note: This doesn't actually verify the email but tests the endpoint
        """

        dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTUwOTA5NzksInR5cGUiOiJ2ZXJpZmljYXRpb24ifQ.dummy"

        with self.client.get(f"/auth/verify/{dummy_token}", catch_response=True) as response:

            if response.status_code == 400:
                response.success()
                logging.info("Verification endpoint tested with expected failure")
            elif response.status_code == 200:
                logging.info("Surprisingly successful verification")
            else:
                logging.error(f"Unexpected response: {response.status_code}, {response.text}")
                response.failure(f"Verification failed with unexpected status: {response.status_code}")
