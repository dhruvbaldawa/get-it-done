from box import Box

from get_it_done.external.google_oauth2 import get_google_client
from get_it_done.models import OAuthUser


async def task_load_gmail_messages():
    client = get_google_client()

    for user in OAuthUser.select():
        access_info = Box(await client.refresh_access_token(user.refresh_token))

        access_token = user.access_token
        email_threads = Box(await client.get_email_threads(access_token, 'in:inbox is:unread'))
        print(email_threads.to_json())
