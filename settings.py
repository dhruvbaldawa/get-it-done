# -*- coding: utf-8 -*-

"""Global settings for the project"""

import os.path

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

__BASE_PACKAGE__ = "get_it_done"

settings = {}

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

if settings["debug"]:
    import logging
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
