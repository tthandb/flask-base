import os
import sys
import random
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
from session import db_session, db_engine, session_scope # noqa
from services.user import UserService # noqa
from faker import Faker # noqa


class SeedData(object):
    def __init__(self):
        self.engine = db_engine()
        db_session.configure(bind=self.engine)
        self.session = db_session()
        self.fake = Faker('en_US')

    def seed_user(self, number_user=10):
        print('Start seed user')
        user_service = UserService(session=self.session)
        user_infos = []
        if number_user <= 0:
            number_user = 10
        domain_list = set()
        for i in range(number_user):
            user_info = {
                'name': domain_name,
                'email': self.fake.email(),
                'password': self.fake.sha256(),
                'status': 'ACTIVE',
            }
            user_infos.append(user_info)

        with session_scope(self.session):
            user_service.bulk_create(user_infos)

        print('Seed shop done')


if __name__ == '__main__':
    seed_data = SeedData()
    seed_data.seed_user(50)
