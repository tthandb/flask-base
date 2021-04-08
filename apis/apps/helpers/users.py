from flask import request
from functools import wraps
from common.errors import UPermissionDenied


def verify_user_in_request(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.context['jwt_data']:
            self.context['user_id'] = self.context['jwt_data'].get('client_id')
        return fn(*args, **kwargs)
    return wrapper
