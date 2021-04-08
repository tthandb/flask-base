from datetime import datetime
import pytz
from common.errors import UBadRequest
from common.helpers.time_helper import utc_hour_now
from database.session import db_engine
from sqlalchemy.orm import sessionmaker
from middlewares.redis_client import RedisClient
from functools import wraps


def connect_database(func):
    @wraps(func)
    def func_wapper(*args, **kwargs):
        self = args[0]
        engine = db_engine()
        db_session = sessionmaker(bind=engine)
        session = db_session()
        self.session = session
        try:
            return func(*args, **kwargs)
        finally:
            self.session.close()
    return func_wapper


class BaseWorker(object):
    def validate_message(self, message, check_id=True):
        payload = message.get('payload', {})
        update_timestamp = message.get('update_time')
        try:
            update_time = datetime.utcfromtimestamp(int(update_timestamp))
        except Exception:
            raise UBadRequest('Invalid update_time')

        update_data = payload.get('data')
        if not (update_data and update_time):
            raise UBadRequest(
                'Missing required params: payload or update_time'
            )

        if (check_id and 'id' not in update_data):
            raise UBadRequest(
                'Missing required params: id'
            )

        return payload, update_time

    def get_redis_client(self):
        if not hasattr(self, 'redis_client'):
            self.redis_client = RedisClient().get_client()
        return self.redis_client

    def get_redis_ad_key(self, datalake_ad_id):
        return 'ad_datalake_{}'.format(datalake_ad_id)
