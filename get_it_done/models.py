from datetime import datetime

from peewee import *
from playhouse.postgres_ext import ArrayField

from .constants import MINUTES
from .database import database


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
    state = CharField(default='initial')
    sent_at = TimestampField(default=0)



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
