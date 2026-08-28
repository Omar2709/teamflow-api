from .settings import *


# Fast password hashing exclusively for automated tests.
# Never use MD5PasswordHasher in development or production.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]