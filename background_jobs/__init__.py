import os
import time
import uuid
import traceback
from functools import wraps
from sqlalchemy.orm import sessionmaker
from database.session import db_engine
from middlewares.logger import write_log


def connect_database(func):
    @wraps(func)
    def func_wapper(*args, **kwargs):
        self = args[0]

        request_id = str(uuid.uuid4())
        extra_log = {
            'request_id': request_id,
            'tags': request_id,
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'request_type': 'BACKGROUND_JOB',
            'action': self.__class__.__name__
        }
        write_log(
            raw_message='Start Background job at {}'.format(time.time()),
            extra=extra_log
        )

        engine = db_engine()
        db_session = sessionmaker(bind=engine)
        session = db_session()
        self.session = session

        try:
            result = func(*args, **kwargs)
            write_log(
                raw_message='End Background job at {}'.format(time.time()),
                extra=extra_log
            )
            return result
        except Exception as error:
            write_log(
                raw_message='Has exception: {}'.format(traceback.format_exc()),
                extra=extra_log
            )
            raise error
        finally:
            self.session.close()
    return func_wapper
