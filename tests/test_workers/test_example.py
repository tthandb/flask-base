# import copy
# import time
# import datetime
# from common.helpers.dict_ultility import to_dict
# from common.helpers.time_helper import utc_hour_now
# from workers.example import Example
# from database.session import db_engine, db_flask_session


# class TestExample(object):
#     @classmethod
#     def setup_class(cls):
#         from factories.user import UserFactory

#         def setup_before_test():
#             engine = db_engine()
#             db_flask_session.configure(bind=engine)
#             cls.session_factory = db_flask_session
#             cls.session = cls.session_factory()
#             user = UserFactory.create(
#                 email="dev@example.com",
#                 status='ACTIVE'
#             )
#             cls.session.refresh(user)
#             setup_for_user(user)

#             cls.worker_object = Example()
#             cls.data = {
#                 'action': 'WORKER_EXAMPLE',
#                 'payload': {
#                     'user': user
#                 },
#                 'update_time': int(time.time())
#             }

#         def setup_for_user(user):
#             return user

#         setup_before_test()

#     @classmethod
#     def teardown_class(cls):
#         cls.session_factory.close_all()
