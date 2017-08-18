import datetime

from peewee import *
from playhouse.postgres_ext import ArrayField
from .database import database


class BaseModel(Model):
    created_at = TimestampField(default=datetime.datetime.now)
    updated_at = TimestampField()

    class Meta:
        database = database

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
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


class GmailThread(BaseModel):
    id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(OAuthUser, related_name='gmail_threads')
    labels = ArrayField(field_class=CharField)
    state = CharField()
    sent_at = TimestampField()

    STATES = ('1d', '3d', '7d', '10d', '14d', 'archived')
