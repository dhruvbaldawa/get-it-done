# -*- coding: utf-8 -*-

from .handlers import base, auth_google


url_patterns = [
    (r"/", base.MainHandler),
    (r"/auth/google/", auth_google.GoogleOAuth2LoginHandler),
]
