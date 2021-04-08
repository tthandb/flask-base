import os
import sys
import time
import jwt
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir
    )
)
from app import init_app, db # noqa
from database.session import db_engine # noqa
from common.helpers.jwt import generate_token # noqa
from common.helpers.dict_ultility import to_dict # noqa
from common.helpers.password import hash_password # noqa


class MockHTTPResponse(object):
    def __init__(self, status_code, response_json={}):
        self.status_code = status_code
        self.response_json = response_json

    def json(self, *args, **kwargs):
        return self.response_json


class BaseAPITest(object):
    client = None
    session_factory = None
    context = None

    @classmethod
    def setup_class(cls):
        """
        Setup flask and truncate database
        """
        flask_app = init_app('test')

        cls.context = flask_app.app_context()
        cls.context.push()
        cls.client = flask_app.test_client()
        cls.session_factory = db.session_factory

    @classmethod
    def teardown_class(cls):
        """
        Close session and remove flask context
        """
        cls.session_factory.close_all()
        cls.context.pop()

    @classmethod
    def create_admin_product(cls):
        password = hash_password('12345678')
        session = cls.session_factory
        from factories.admin import AdminFactory
        product_admin = AdminFactory.create(
            email='product_admin_{}@example.com'.format(time.time()),
            password=password,
            status='ACTIVE',
            admin_roles=['PRODUCT']
        )
        session.refresh(product_admin)
        cls.product_admin = to_dict(product_admin)
        cls.product_admin_token = generate_token({
            'admin_id': product_admin.id,
            'client_type': 'ADMIN',
            'login_at': time.time()
        })

    @classmethod
    def create_admin_financial(cls):
        password = hash_password('12345678')
        session = cls.session_factory
        from factories.admin import AdminFactory
        financial_admin = AdminFactory.create(
            email='financial_admin_{}@example.com'.format(time.time()),
            password=password,
            status='ACTIVE',
            admin_roles=['FINANCIAL']
        )
        session.refresh(financial_admin)
        cls.financial_admin = to_dict(financial_admin)
        cls.financial_admin_token = generate_token({
            'admin_id': financial_admin.id,
            'client_type': 'ADMIN',
            'login_at': time.time()
        })

    @classmethod
    def create_admin_am(cls):
        password = hash_password('12345678')
        session = cls.session_factory
        from factories.admin import AdminFactory
        am_admin = AdminFactory.create(
            email='am_admin_{}@example.com'.format(time.time()),
            password=password,
            status='ACTIVE',
            admin_roles=['AM']
        )
        session.refresh(am_admin)
        cls.am_admin = to_dict(am_admin)
        cls.am_admin_token = generate_token({
            'admin_id': am_admin.id,
            'client_type': 'ADMIN',
            'login_at': time.time()
        })

    @classmethod
    def generate_internal_token(cls, system):
        payload = {
            'system': system,
            'generate_time': int(time.time())
        }
        internal_token = jwt.encode(
            payload,
            os.getenv('INTERNAL_API_JWT_SECRET_KEY'),
            algorithm=os.getenv('JWT_ALGORITHM')
        ).decode('utf-8')
        return internal_token
