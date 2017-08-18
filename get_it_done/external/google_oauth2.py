import json
import logging
from http import HTTPStatus
from urllib.parse import urlencode

from aiohttp import ClientSession
from tornado.options import options

logger = logging.getLogger(__name__)


class ClientError(Exception):
    def __init__(self, status, body, headers):
        self.status = status
        self.body = body
        self.headers = headers

    def __str__(self):
        return f'Client error: {self.status} {self.body} with headers {self.headers}'


def get_google_client():
    return GoogleOAuth2Client(options.google_client_key, options.google_client_secret)


class GoogleOAuth2Client(object):
    BASE_URL = 'https://www.googleapis.com'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    @staticmethod
    def _build_authorization_header(access_token):
        return {
            'Authorization': f'Bearer {access_token}',
        }

    async def request(self, method, url, params=None, data=None, headers=None):
        logger.debug('Making Google OAuth request %s %s', method, url)
        async with ClientSession(raise_for_status=True) as session:
            async with session.request(
                method=method,
                url=self.BASE_URL + url,
                params=params,
                data=data,
                headers=headers,
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    raise ClientError(resp.status, resp.content, resp.headers)
                return await resp.json()

    async def refresh_access_token(self, refresh_token):
        data = urlencode({
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
        })
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        resp = await self.request('POST', '/oauth2/v4/token', data=data, headers=headers)

        return resp

    async def get_email_threads(self, access_token, user='me', search='', page_token=''):
        params = {
            'pageToken': page_token,
            'q': search,
        }
        headers = self._build_authorization_header(access_token)

        resp = await self.request('GET', f'/gmail/v1/users/{user}/threads', params=params, headers=headers)

        return resp

    async def get_email_thread(self, access_token, thread_id, user='me', format='metadata'):
        params = {
            'format': format
        }
        headers = self._build_authorization_header(access_token)

        resp = await self.request('GET', f'/gmail/v1/users/{user}/threads/{thread_id}', params=params, headers=headers)

        return resp

    async def change_thread_label(self, access_token, thread_id, user='me', add_labels=None, remove_labels=None):
        body = {}
        if add_labels is not None:
            body['addLabelIds'] = list(add_labels)

        if remove_labels is not None:
            body['removeLabelIds'] = list(remove_labels)
        body = json.dumps(body)
        headers = self._build_authorization_header(access_token)
        headers['Content-Type'] = 'application/json'

        resp = await self.request(
            'POST',
            f'/gmail/v1/users/{user}/threads/{thread_id}/modify',
            data=body,
            headers=headers,
        )

        return resp
