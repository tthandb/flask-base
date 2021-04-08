import time
from datetime import datetime
from datetime import timedelta
from database.models.user import User, UserStatus
from database.services.base import BaseService
from database.services.user import UserService
from common.helpers.jwt import generate_token
from common.helpers.password import verify_password
from common.helpers.password import hash_password
from common.errors import UPermissionDenied, UBadRequest
from common.helpers.jwt import ClientType


class AuthService(BaseService):
    DAY_EXPIRE = 1
    MAX_NUMBER_OF_DEVICES = 5

    def __init__(self, session):
        self.session = session
        self.user_service = UserService(self.session)

    def create_user_with_token(self, ui_data):
        _user_fields = self._user_fields(ui_data)
        user = self.user_service.get_user_by_domain(
            _user_fields['email']
        )
        if user:
            raise UBadRequest('User already exists !!')
        _user_fields['password'] = hash_password(_user_fields['password'])
        user = self.user_service.create(**_user_fields)
        token = self._create_token(user, {
            'sub': user.email,
            'client_id': user.id,
            'client_type': ClientType.User.value
        })
        return token, user

    def login(self, ui_data):
        _user_fields = self._user_fields(ui_data)
        user = self.user_service.get_user_by_email(
            _user_fields['email']
        )
        if not user or not verify_password(
            _user_fields['password'], user.password):
            raise UPermissionDenied()
        if user.status != UserStatus.ACTIVE.value:
            raise UPermissionDenied()
        token = self._create_token(user, {
            'sub': user.email,
            'client_id': user.id,
            'client_type': ClientType.User.value
        })
        self._clean_old_tokens(user)
        self.user_service.update(
            user,
            tokens=user.tokens
        )
        return token, user.to_json_except_keys()

    def _create_token(self, obj, payload, **token_extra):
        now = datetime.now()
        expiry = datetime.now() + timedelta(days=AuthService.DAY_EXPIRE)
        payload['iat'] = datetime.timestamp(now)
        payload['exp'] = datetime.timestamp(expiry)
        token = generate_token(payload)
        tokens = obj.tokens or {}

        tokens[payload['client_id']] = {
            'token': hash_password(token),
            'expiry': payload['exp']
        }
        obj.tokens = tokens
        return token

    def _clean_old_tokens(self, obj):
        if obj.tokens and self._max_client_tokens_exceeded(obj):
            obj.tokens = sorted(
                obj.tokens.items(),
                key=lambda kv: kv[1]['expiry']
            )
            while self._max_client_tokens_exceeded(obj):
                obj.tokens.pop(0)

    def _max_client_tokens_exceeded(self, obj):
        tokens = obj.tokens or {}
        return len(tokens) > AuthService.MAX_NUMBER_OF_DEVICES

    def _user_fields(self, ui_data):
        return {
            'email': ui_data['email'],
            'password': ui_data['password']
        }
