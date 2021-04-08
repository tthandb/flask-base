from flask import Blueprint
from common.api import UApi
from apis.example import Example
from apis.apps.views.users import Users
from apis.sessions.views.auth import Auth


routes = Blueprint('routes', __name__)
api_routes = UApi(routes)

api_routes.add_resource(Example, '/example')
api_routes.add_resource(Users, '/apps/users')
api_routes.add_resource(Auth, '/services/auth')
