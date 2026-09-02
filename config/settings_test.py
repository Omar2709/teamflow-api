from .settings import *


ALLOWED_HOSTS = [
    "testserver",
    "localhost",
    "127.0.0.1",
]

# Fast password hashing exclusively for automated tests.
# Never use MD5PasswordHasher in development or production.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]