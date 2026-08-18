from .base import *  # noqa: F403,F401
from config.email import build_email_config

DEBUG = True
globals().update(build_email_config(debug=True))

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
