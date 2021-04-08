from common.api import UResource
from common.validator import validate_body
# from common.errors import UNotFound, UBadRequest
from app import db
from database.session import session_scope
from database.services.apps.auth import AuthService
from apis.sessions.validators.auth import RequestLoginSchema


class Auth(UResource):
    def __init__(self):
        self.session = db.session_factory()
        self.auth_service = AuthService(self.session)

    @validate_body(RequestLoginSchema)
    def post(self):
        with session_scope(self.session):
            token, user = self.auth_service.login(self.body)
        return {
            'message': 'Login successfully',
            'token': token,
            'data': user
        }
