import os
import sys
import psycopg2
import pytest
import faktory
from unittest.mock import Mock
import sentry_sdk
from alembic.config import Config
from alembic import command
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), os.pardir
    )
)
from common.helpers import mail_helper # noqa
from middlewares.sendgrid_email import SendGridService # noqa
from middlewares.redis_client import RedisClient # noqa
from middlewares.fraudlabpro_client import FraudlabproClient # noqa


class MockFaktory():
    def __enter__(*args, **kwargs):
        return MockFaktory()

    def __exit__(*args, **kwargs):
        return MockFaktory()

    def __getattribute__(*args, **kwargs):
        return MockFaktory()


class MockRedis():
    def set(*args, **kwargs):
        return None

    def get(*args, **kwargs):
        return None


@pytest.fixture(scope='session')
def my_setup(request):
    test_env_path = '{}/.testing.env'.format(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), os.pardir
        )
    )
    load_dotenv(test_env_path, override=True)
    os.environ['ENVIRONMENT_NAME'] = 'test'

    db_name = 'ucella_test_database'
    con = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('DBUSER'),
        host=os.getenv('DBHOST'),
        password=os.getenv('DBPASSWORD'),
        port=os.getenv('DBPORT')
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname='{}';".format(db_name)
    )
    result = cur.fetchall()
    if result:
        if result[0][0] == 1:
            cur.execute(sql.SQL('DROP DATABASE {}').format(
                sql.Identifier(db_name))
            )

    cur.execute(sql.SQL('CREATE DATABASE {}').format(
        sql.Identifier(db_name))
    )
    cur.execute(
        sql.SQL("ALTER USER {} SET timezone TO 'UTC';").format(
            sql.Identifier(os.getenv('DBUSER'))
        )
    )

    os.environ['CELLAS_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.getenv('DBUSER'), os.getenv('DBPASSWORD'), os.getenv('DBHOST'),
        os.getenv('DBPORT'), db_name
    )

    migrations_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir
    )
    config_file = os.path.join(migrations_dir, 'alembic.ini')
    config = Config(config_file)
    command.upgrade(config, 'head')

    # mock
    sentry_sdk.init = Mock(return_value=None)
    faktory.connection = Mock(return_value=MockFaktory())
    mail_helper.create_group_mail = Mock(return_value=None)
    SendGridService.send_email = Mock(return_value=None)
    RedisClient.__init__ = Mock(return_value=None)
    RedisClient.get_client = Mock(return_value=MockRedis())
    FraudlabproClient.check_fraud = Mock(return_value=50)

    def fin():
        pass
    request.addfinalizer(fin)
