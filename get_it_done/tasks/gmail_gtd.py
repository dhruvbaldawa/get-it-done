import logging
from asyncio import gather

from box import Box

from ..database import database
from ..external.google_oauth2 import get_google_client
from ..models import GmailThread, OAuthUser

logger = logging.getLogger(__name__)


async def task_load_gmail_messages():
    client = get_google_client()

    async def extract_email_threads(access_token, user_id):
        email_threads = await client.get_email_threads(access_token, user_id, 'in:inbox is:unread')
        for t in email_threads['threads']:
            yield t

    for user in OAuthUser.select():
        logger.info("Processing mails for process user %s", user.email)
        logger.info("Fetching user emails")

        email_threads = await gather(*[client.get_email_thread(user.token, thread['id'])
                                       async for thread in extract_email_threads(user.token, user.id)])

        with database.transaction():
            for email_thread in email_threads:
                thread_box = Box(email_thread, camel_killer_box=True)

                thread, _ = GmailThread.get_or_create(id=thread_box.id, user=user)

                thread.labels = thread_box.messages[-1].label_ids
                thread.sent_at = int(thread_box.messages[-1].internal_date) / 1000
                thread.save()


def task_gmail_messages_next_cycle():
    logger.info('Running next cycle task for messages')
    for message in GmailThread.select().where(GmailThread.state != GmailThread.STATE_FINAL):
        message.next()

async def task_chronos_test():
    logger.info('I was running')
