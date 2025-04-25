import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/insurance")

# Email settings
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USERNAME = "ilosipenko@edu.hse.ru"
EMAIL_PASSWORD = "eolpamhbdktuqphg"

# Security settings
SECRET_KEY = "549nc4eg=t92&)b)_ebhlpk)b8i)-ju6(8uqt*(g!8gi1fy8!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Frontend URL for email verification
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
