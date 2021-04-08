from common.api import UResource
from common.helpers.dict_ultility import to_dict
from common.validator import validate_body
from common.errors import UNotFound, UBadRequest
from app import db
from database.session import session_scope
from database.services.user import UserService
from database.services.apps.auth import AuthService
from apis.apps.helpers.users import verify_user_in_request
from common.helpers.jwt import required_jwt
from apis.apps.validators.users import RequestCreateUserSchema, RequestUpdateUserSchema
from flask import g


class Users(UResource):

    def __init__(self):
        self.session = db.session_factory()
        self.context = g.context
        self.user_service = UserService(self.session)
        self.auth_service = AuthService(self.session)

    @validate_body(RequestCreateUserSchema)
    def post(self):
        with session_scope(self.session):
            token, user = self.auth_service.create_user_with_token(self.body)
        return {
            'message': 'Create Successfully',
            'token': token,
            'data': user.to_json_except_keys()
        }, 201

    @required_jwt
    @validate_body(RequestUpdateUserSchema)
    @verify_user_in_request
    def patch(self):
        ui_data = self.body.get('user')
        with session_scope(self.session):
            user_id = self.user_service.update_my_user(ui_data)
        return {
            'message': 'Update User Successfully',
            'data': user_id
        }, 200
