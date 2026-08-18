import os

from .base import *  # noqa: F403,F401
from config.email import build_email_config

DEBUG = False
globals().update(build_email_config(debug=False))

# Set USE_HTTPS=true once the API is behind TLS (ALB/nginx). HTTP-only IP access needs false.
USE_HTTPS = os.getenv("USE_HTTPS", "false").lower() == "true"
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
