from peewee_async import PostgresqlDatabase, Manager
from tornado.options import options


database = PostgresqlDatabase(
    options.db_name,
    autorollback=True,
    host=options.db_host,
    user=options.db_user,
    password=options.db_pass,
)

objects = Manager(database)


def create_tables():
    from .models import OAuthUser, GmailThread
    OAuthUser.create_table()
    GmailThread.create_table()


def drop_tables():
    from .models import OAuthUser, GmailThread
    GmailThread.drop_table()
    OAuthUser.drop_table()
