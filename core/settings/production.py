from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "13.232.79.134",
    "task.thedeepseafood.com",
]  # Example - Need to Replace with the server IP - Do not remove localhost

# Database
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": os.getenv("NAME"),  # noqa: F405
#         "USER": os.getenv("USER"),  # noqa: F405
#         "PASSWORD": os.getenv("PASSWORD"),  # noqa: F405
#         "HOST": os.getenv("HOST"),  # noqa: F405
#         "PORT": os.getenv("PORT"),  # noqa: F405
#         "OPTIONS": {
#             "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
