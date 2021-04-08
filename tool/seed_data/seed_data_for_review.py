import os
import sys
import time
from dotenv import load_dotenv
sys.path.append(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir))
from common.helpers.password import hash_password # noqa
from database.session import db_session, db_engine, session_scope # noqa
from database.services.shop import UserService # noqa

def seed_data():
    engine = db_engine()
    db_session.configure(bind=engine)
    session = db_session()

    user_service = UserService(session)

    password = '12345678'
    password_hashed = hash_password(password)
    with session_scope(session):
        user_service.create(
            email='dev@example.com',
            name='Example',
            password=password_hashed,
            status='ACTIVE'
        )

if __name__ == '__main__':
    load_dotenv()
    environment = os.getenv('ENVIRONMENT', 'development'),
    if environment is 'review':
        seed_data()
