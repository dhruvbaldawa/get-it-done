from datetime import datetime
from functools import partial

import logging
from peewee import *
from playhouse.postgres_ext import ArrayField
from transitions import Machine

from .constants import MINUTES, DAYS
from .database import database

logger = logging.getLogger(__name__)

class BaseModel(Model):
    created_at = TimestampField(default=datetime.now)
    updated_at = TimestampField()

    class Meta:
        database = database

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)


class OAuthUser(BaseModel):
    id = CharField(unique=True, primary_key=True)
    email = CharField(unique=True)
    name = CharField()
    access_token = CharField()
    token_expiry = TimestampField()
    refresh_token = CharField(null=True)

    @classmethod
    def update_user_info(cls, user_id, **user_info):
        try:
            with database.atomic():
                OAuthUser.create(id=user_id, **user_info)
        except IntegrityError:
            user_info.pop('refresh_token')
            OAuthUser.update(**user_info).where(OAuthUser.id == user_id).execute()

    @classmethod
    def update_credentials(cls, user_id, access_token, token_expiry):
        OAuthUser.update(access_token=access_token, token_expiry=token_expiry)\
            .where(OAuthUser.id == user_id).execute()

    def is_token_expiring(self):
        return (self.token_expiry - datetime.now()).total_seconds() <= (30 * MINUTES)


class GmailThread(BaseModel):
    STATE_INITIAL = 'initial'
    STATE_1D = '1d'
    STATE_3D = '3d'
    STATE_7D = '7d'
    STATE_10D = '10d'
    STATE_14D = '14d'
    STATE_ARCHIVED = 'archived'

    STATES = (STATE_INITIAL, STATE_1D, STATE_3D, STATE_7D, STATE_10D, STATE_14D, STATE_ARCHIVED)

    id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(OAuthUser, related_name='gmail_threads')
    labels = ArrayField(field_class=CharField, default=[])
    state = CharField(default=STATE_INITIAL)
    sent_at = TimestampField(default=0)

    def _generate_transitions(self):
        return [
            {
                'trigger': 'next',
                'source': [self.STATE_INITIAL, self.STATE_14D, self.STATE_ARCHIVED],
                'dest': self.STATE_ARCHIVED,
                'conditions': partial(self.has_time_elapsed, '15d'),
                'after': self.archive,
            },
        ] + [
            {
                'trigger': 'next',
                'source': self.STATE_INITIAL,
                'dest': state,
                'conditions': partial(self.has_time_elapsed, state),
                'after': partial(self.change_labels, self.STATE_INITIAL, state),
            }
            for state in reversed((self.STATE_1D, self.STATE_3D, self.STATE_7D, self.STATE_10D, self.STATE_14D))
        ] + [
            {
                'trigger': 'next',
                'source': source,
                'dest': destination,
                'conditions': partial(self.has_time_elapsed, destination),
                'after': partial(self.change_labels, source, destination),
            }
            for source, destination in zip(
                (self.STATE_INITIAL, self.STATE_1D, self.STATE_3D, self.STATE_7D, self.STATE_10D),
                (self.STATE_1D, self.STATE_3D, self.STATE_7D, self.STATE_10D, self.STATE_14D),
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.machine = Machine(
            model=self,
            states=self.STATES,
            initial=self.STATE_INITIAL,
            transitions=self._generate_transitions(),
            after_state_change='save',
        )

    def has_time_elapsed(self, time):
        time = int(time[:-1])
        return (datetime.now() - self.sent_at).total_seconds() > time * DAYS

    def change_labels(self, source, destination):
        logger.debug('changing labels from %s to %s', source, destination)

    def archive(self):
        logger.debug('Archiving %s', self.id)
