from locust import HttpUser, task, between
import random
import json
import logging


class RecommendationUser(HttpUser):
    """
    Locust user class for testing recommendation endpoints
    """
    wait_time = between(2, 5)

    def on_start(self):
        """Initialize with random user data and login"""
        self.user_id = random.randint(10000, 99999)
        self.email = f"loadtest_{self.user_id}@example.com"
        self.password = "LoadTest123!"
        self.token = None

        self.login()

        self.user_data = self.generate_random_user_data()
        self.recommendation_data = self.generate_recommendation_request()

    def login(self):
        """Login to get an authentication token"""
        login_data = {
            "email": self.email,
            "password": self.password
        }

        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                logging.info(f"Successfully logged in user: {self.email}")
            else:

                logging.info(f"Proceeding without authentication")

    def generate_random_user_data(self):
        """Generate random user profile data"""
        return {
            "user_name": f"user_{self.user_id}",
            "first_name": "Load",
            "last_name": "Test",
            "age": random.randint(18, 75),
            "gender": random.choice(["male", "female", "non-binary"]),
            "occupation": random.choice(["Engineer", "Doctor", "Teacher", "Accountant", "Artist"]),
            "income": random.randint(30000, 200000),
            "marital_status": random.choice(["single", "married", "divorced"]),
            "has_children": random.choice([True, False]),
            "has_vehicle": random.choice([True, False]),
            "has_home": random.choice([True, False]),
            "has_medical_conditions": random.choice([True, False]),
            "travel_frequency": random.choice(["rarely", "occasional", "frequent"])
        }

    def generate_recommendation_request(self):
        """Generate recommendation request data based on user profile"""
        return {
            "age": self.user_data["age"],
            "gender": self.user_data["gender"],
            "occupation": self.user_data["occupation"],
            "income": self.user_data["income"],
            "marital_status": self.user_data["marital_status"],
            "has_children": self.user_data["has_children"],
            "has_vehicle": self.user_data["has_vehicle"],
            "has_home": self.user_data["has_home"],
            "has_medical_conditions": self.user_data["has_medical_conditions"],
            "travel_frequency": self.user_data["travel_frequency"]
        }

    @task(10)
    def get_recommendations(self):
        """Task to get insurance recommendations"""
        with self.client.post(
                "/recommendation/get_recommendations",
                json=self.recommendation_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                recommendations = response.json()
                if len(recommendations) > 0:
                    logging.info(f"Got {len(recommendations)} recommendations")

                    if random.random() < 0.7:
                        self.check_recommendation(recommendations[0]["product_id"])
                else:
                    logging.warning("No recommendations returned")
            else:
                logging.error(f"Failed to get recommendations: {response.status_code}, {response.text}")
                response.failure(f"Get recommendations failed with status code: {response.status_code}")

    def check_recommendation(self, product_id):
        """Record that a user checked a recommendation"""
        check_data = {
            "product_id": product_id,
            "user_email": self.email
        }

        with self.client.post(
                "/recommendation/check_recommendation",
                json=check_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                logging.info(f"Successfully checked product ID: {product_id}")
            elif response.status_code == 404:

                response.success()
                logging.info(f"User not found when checking product: {product_id}")
            else:
                logging.error(f"Failed to check recommendation: {response.status_code}, {response.text}")
                response.failure(f"Check recommendation failed with status code: {response.status_code}")

    @task(5)
    def update_user_profile(self):
        """Task to update user profile"""
        if not self.token:
            return

        update_data = {}
        fields = list(self.user_data.keys())
        num_fields_to_update = random.randint(1, 3)

        for _ in range(num_fields_to_update):
            field = random.choice(fields)

            if field == "age":
                update_data[field] = random.randint(18, 75)
            elif field == "income":
                update_data[field] = random.randint(30000, 200000)
            elif field in ["has_children", "has_vehicle", "has_home", "has_medical_conditions"]:
                update_data[field] = random.choice([True, False])
            elif field == "gender":
                update_data[field] = random.choice(["male", "female", "non-binary"])
            elif field == "marital_status":
                update_data[field] = random.choice(["single", "married", "divorced"])
            elif field == "occupation":
                update_data[field] = random.choice(["Engineer", "Doctor", "Teacher", "Accountant", "Artist"])
            elif field == "travel_frequency":
                update_data[field] = random.choice(["rarely", "occasional", "frequent"])

            if field in update_data:
                self.user_data[field] = update_data[field]

        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.put(
                "/user/update_info",
                json=update_data,
                headers=headers,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                logging.info(f"Successfully updated user profile")

                self.recommendation_data = self.generate_recommendation_request()
            elif response.status_code == 401:

                response.success()
                self.login()
            else:
                logging.error(f"Failed to update profile: {response.status_code}, {response.text}")
                response.failure(f"Update profile failed with status code: {response.status_code}")
