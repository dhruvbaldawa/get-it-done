import time

import logging
from asyncio import gather

from box import Box

from ..database import database
from ..external.google_oauth2 import get_google_client
from ..models import OAuthUser, GmailThread

logger = logging.getLogger(__name__)

async def task_load_gmail_messages():
    client = get_google_client()

    async def check_for_token_expiry(user):
        if user.is_token_expiring():
            logger.info("User token expiring, lets do a refresh")
            access_info = Box(await client.refresh_access_token(user.refresh_token))
            user.access_token = access_info.access_token
            user.token_expiry = time.time() + access_info.expires_in
            user.save()

    async def extract_email_threads(access_token, user_id):
        email_threads = await client.get_email_threads(access_token, user_id, 'in:inbox is:unread')
        for t in email_threads['threads']:
            yield t

    for user in OAuthUser.select():
        logger.info("Processing mails for process user %s", user.email)

        await check_for_token_expiry(user)

        logger.info("Fetching user emails")

        email_threads = await gather(*[client.get_email_thread(user.access_token, thread['id'])
                                     async for thread in extract_email_threads(user.access_token, user.id)])

        with database.transaction():
            for email_thread in email_threads:
                thread_box = Box(email_thread, camel_killer_box=True)

                thread, _ = GmailThread.get_or_create(id=thread_box.id, user=user)

                thread.labels = thread_box.messages[0].label_ids
                thread.sent_at = int(thread_box.messages[0].internal_date)/1000
                thread.save()

