import time

from box import Box
from tornado.auth import GoogleOAuth2Mixin
from tornado.options import options
from tornado.web import RequestHandler

from ..models import OAuthUser


class GoogleOAuth2LoginHandler(RequestHandler, GoogleOAuth2Mixin):
    OAUTH_URL = 'https://www.googleapis.com/oauth2/v2'
    OAUTH_SCOPES = (
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://mail.google.com/',
        'https://www.googleapis.com/auth/gmail.insert',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
    )

    async def fetch_tokens(self, code):
        return await self.get_authenticated_user(
            redirect_uri=f'{options.weburl}/auth/google/',
            code=code,
        )

    async def fetch_user_info(self, access_token):
        return await self.oauth2_request(
            f'{self.OAUTH_URL}/userinfo',
            access_token=access_token,
        )

    async def get(self):
        if self.get_argument('code', False):
            access = await self.fetch_tokens(self.get_argument('code'))
            access_info = Box(access, default_box=True, default_box_attr=None)

            user = await self.fetch_user_info(access_info.access_token)
            user = Box(user)

            OAuthUser.update_user_info(
                email=user.email,
                user_id=user.id,
                name=user.name,
                access_token=access_info.access_token,
                token_expiry=time.time() + access_info.expires_in,
                refresh_token=access_info.refresh_token,
            )
            self.redirect("/")
        else:
            await self.authorize_redirect(
                redirect_uri=f'{options.weburl}/auth/google/',
                client_id=self.settings['google_oauth']['key'],
                scope=self.OAUTH_SCOPES,
                response_type='code',
                extra_params={
                    'access_type': 'offline',
                    'include_granted_scopes': 'true',
                    'approval_prompt': 'auto',
                },
            )
