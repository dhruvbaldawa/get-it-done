# -*- coding: utf-8 -*-

"""Global settings for the project"""

import os.path
import logging.config

from envparse import env
from tornado.options import define


define("port", default=8000, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")
define("db-host", default="localhost", help="Database host", type=str)
define("db-user", default="get_it_done", help="Database user", type=str)
define("db-pass", default="get_it_done", help="Database password", type=str)
define("db-name", default="get_it_done", help="Database name", type=str)
define("weburl", default="http://localhost:8000", help="URL of the website", type=str)
define("google-client-key", default=env("GOOGLE_OAUTH_KEY"), help="Google Client Key", type="str")
define("google-client-secret", default=env("GOOGLE_OAUTH_SECRET"), help="Google Client Secret", type="str")

__BASE_PACKAGE__ = "get_it_done"

settings = dict()

settings["debug"] = True
settings["cookie_secret"] = "U14CjAyX9uavn9myPVGG9w8gd"
settings["login_url"] = "/login"
settings["static_path"] = os.path.join(os.path.dirname(__file__), __BASE_PACKAGE__, "static")
settings["template_path"] = os.path.join(os.path.dirname(__file__), __BASE_PACKAGE__, "templates")
settings["xsrf_cookies"] = False
settings["google_oauth"] = {
    "key": env("GOOGLE_OAUTH_KEY"),
    "secret": env("GOOGLE_OAUTH_SECRET"),
}

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'tornado': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'get_it_done': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'peewee': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
})

if settings["debug"]:
    import logging
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
