import os
import jwt
import pytz
import time
from enum import Enum
from functools import wraps
from flask import request, g
from common.errors import UPermissionDenied
from common.helpers.enum_helper import get_names_of_enum
from database.models.user import UserStatus
from database.services.user import UserService

default_header_name = os.getenv('JWT_HEADER_NAME')
default_header_type = os.getenv('JWT_HEADER_TYPE')
default_secret_key = os.getenv('JWT_SECRET_KEY')
default_algorithm = os.getenv('JWT_ALGORITHM')


class ClientType(Enum):
    User = 'USER'
    ADMIN = 'ADMIN'

def verify_jwt_in_request(header_name='Authorization',
                          header_type='Bearer'):
    jwt_header = request.headers.get(header_name)
    if not jwt_header:
        raise UPermissionDenied

    # Make sure the header is in a valid format that we are expecting, ie
    # <HeaderName>: <HeaderType(optional)> <JWT>
    parts = jwt_header.split()
    if header_type:
        if parts[0] != header_type or len(parts) != 2:
            raise UPermissionDenied
        encoded_token = parts[1]
    else:
        if len(parts) != 1:
            raise UPermissionDenied
        encoded_token = parts[0]

    return encoded_token


def generate_token(payload=None, **token_extra):
    payload = payload or {}

    env_var = {
        'secret_key': 'JWT_SECRET_KEY',
        'algorithm': 'JWT_ALGORITHM'
    }

    secret_key = os.getenv(env_var['secret_key'])
    algorithm = os.getenv(env_var['algorithm'])

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
    ).decode('utf-8')


def decode_token(encoded_token, leeway=0,
                 secret_key=default_secret_key,
                 algorithm=default_algorithm):
    try:
        data = jwt.decode(
            encoded_token, secret_key,
            algorithms=[algorithm], leeway=leeway
        )
        return data
    except jwt.ExpiredSignatureError:
        raise UPermissionDenied('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise UPermissionDenied('Invalid token. Please log in again.')

def required_jwt(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        self = args[0]
        encoded_token = verify_jwt_in_request()
        self.jwt_data = decode_token(encoded_token)
        client_types = get_names_of_enum(ClientType)
        if self.jwt_data.get('client_type') not in client_types:
            raise UPermissionDenied('Invalid token. Please log in again.')
        client_type = self.jwt_data.get('client_type')
        if client_type == ClientType.User.value:
            user_id = self.jwt_data.get('client_id')
            if not user_id:
                raise UPermissionDenied('Invalid token. Please log in again.')
            user_service = UserService(self.session)
            user = user_service.first(
                id=user_id,
                status=UserStatus.ACTIVE.value
            )
            if not user:
                raise UPermissionDenied('Invalid token. Please log in again.')
            self.user = user
        if not hasattr(self, 'context'):
            self.context = g.context
        self.context['jwt_data'] = self.jwt_data
        return fn(*args, **kwargs)
    return wrapper

def internal_required_jwt(validate_system=None):
    def validate_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            secret_key = os.getenv('INTERNAL_API_JWT_SECRET_KEY')
            algorithm = os.getenv('JWT_ALGORITHM')

            self.jwt_data = decode_jwt(secret_key, algorithm)
            if validate_system:
                internal_system = self.jwt_data.get('system')
                if internal_system != validate_system:
                    raise UPermissionDenied('Permission Denied')

            return func(*args, **kwargs)

        return wrapper
    return validate_decorator


def decode_jwt(secret_key, algorithm):
    encoded_token = verify_jwt_in_request('Authorization', 'Bearer')

    return decode_token(
        encoded_token,
        secret_key=secret_key,
        algorithm=algorithm)
