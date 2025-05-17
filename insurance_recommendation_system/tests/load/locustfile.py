from locust import User, task, between, events
from scenarios.authentication_load import AuthenticationUser
from scenarios.recommendation_load import RecommendationUser
import logging
import os
import time
import csv
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Initialize test environment, set up monitoring, etc.
    """

    if not os.path.exists("results"):
        os.makedirs("results")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    environment.custom_metrics_file = open(f"results/custom_metrics_{timestamp}.csv", "w")
    environment.csv_writer = csv.writer(environment.custom_metrics_file)
    environment.csv_writer.writerow(["timestamp", "metric", "value"])

    logging.info(f"Starting load test with host: {environment.host}")
    if hasattr(environment.runner, "user_classes"):
        logging.info(f"User classes: {', '.join([uc.__name__ for uc in environment.runner.user_classes])}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    Listen for requests and record custom metrics
    """

    if hasattr(events.runner, "environment") and hasattr(events.runner.environment, "csv_writer"):
        if name.startswith("/recommendation"):
            events.runner.environment.csv_writer.writerow([
                datetime.now().isoformat(),
                f"recommendation_{request_type}",
                response_time
            ])


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when a test is started
    """
    logging.info("Load test started")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when a test is stopped
    """
    logging.info("Load test stopped")

    if hasattr(environment, "custom_metrics_file"):
        environment.custom_metrics_file.close()


class MixedLoadTest(User):
    """
    A mixed load test that combines multiple test scenarios
    """

    tasks = {}

    def on_start(self):
        """Choose which type of user to be for this session"""

        import random
        user_type = random.choices(
            [AuthenticationUser, RecommendationUser],
            weights=[30, 70],
            k=1
        )[0]

        self.user = user_type(self.environment)
        self.user.on_start()

    def on_stop(self):
        """Clean up when the user stops"""
        if hasattr(self, "user") and hasattr(self.user, "on_stop"):
            self.user.on_stop()

    @task
    def execute_tasks(self):
        """Execute tasks from the chosen user type"""
        if hasattr(self, "user"):

            import random
            from locust.task import TaskSet

            tasks = self.user.tasks
            if isinstance(tasks, dict):
                tasks = tasks.items()

            total = sum(weight for _, weight in tasks)
            task = random.choices(
                [task for task, _ in tasks],
                weights=[weight / total for _, weight in tasks],
                k=1
            )[0]

            task(self.user)

            if hasattr(self.user, "wait_time"):
                time.sleep(self.user.wait_time())
