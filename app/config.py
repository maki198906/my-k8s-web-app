import os

# os.getenv читает переменную окружения.
# В K8s эти переменные придут из ConfigMap и Secret.
# Локально — либо выставляем вручную, либо используется значение по умолчанию.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
APP_NAME = os.getenv("APP_NAME", "URL Shortener")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
