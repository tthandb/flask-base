import pytz
import signal
from functools import wraps
from common.errors import UTimeoutError
from datetime import datetime, timedelta
from marshmallow import ValidationError


def convert_iso_time_string(time_string):
    if not time_string:
        return
    try:
        space_split = time_string.split(' ')
        new_time_string = time_string
        if len(space_split) > 1:
            new_time_string = '+'.join(space_split)
        time_object = datetime.strptime(
            new_time_string, '%Y-%m-%dT%H:%M:%S%z'
        ).astimezone(pytz.utc)
        return time_object
    except Exception:
        raise ValidationError('Invalid time format')


def convert_date_string(time_string):
    if not time_string:
        return
    try:
        time_object = datetime.strptime(
            time_string, '%Y-%m-%d'
        )
        return time_object.date()
    except Exception:
        raise ValidationError('Invalid time format')


def utc_hour_now():
    return datetime.utcnow().replace(
        minute=0, second=0, microsecond=0, tzinfo=pytz.utc
    )


def get_last_hour_of_day(date_object, timeoffset):
    return datetime(
        year=date_object.year, month=date_object.month, day=date_object.day,
        hour=23, minute=0, second=0, microsecond=0, tzinfo=timeoffset
    ).astimezone(pytz.utc)


def get_date_between_2_date(start_date, end_date):
    if start_date > end_date:
        return []
    delta = end_date - start_date
    return [
        start_date + timedelta(days=i) for i in range(delta.days + 1)
    ]


def format_date(date):
    return date.strftime('%Y-%m-%d')


def timeout(max_timeout=10):
    def validate_timeout_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise UTimeoutError()

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(max_timeout)
            try:
                result = func(*args, **kwargs)
            except UTimeoutError:
                raise UTimeoutError()
            finally:
                signal.alarm(0)

            return result

        return wrapper
    return validate_timeout_decorator
