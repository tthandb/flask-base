from database.models.user import User
from database.services.base import BaseService
from common.errors import UNotFound, UBadRequest
from flask import g


class UserService(BaseService):

    def __init__(self, session, context=None):
        self.session = session
        self.model = User
        try:
            self.context = g.context
        except Exception:
            self.context = None

    def get_user(self, user_id):
        user = self.first(
            id=user_id
        )
        if not user:
            raise UNotFound('User Not Found')
        return user

    def get_user_by_email(self, email):
        return self.first(
            email=email
        )

    def update_my_user(self, ui_data):
        update_fields = {}
        for k in ui_data:
            if k in self._field_update_user():
                update_fields[k] = ui_data[k]
        if len(update_fields) <= 0:
            raise UBadRequest('Nothing To Update')
        user = self.update(self.my_user(), **update_fields)
        return user.id

    def _field_update_user(self):
        return {
            'name',
        }

    def update_password(self):
        pass

    def update_status(self):
        pass

    def my_user_id(self):
        return self.context['user_id']

    def my_user(self):
        return self.get_user(self.my_user_id())

    def index_user(self, limit=10, offset=0, **kwargs):
        query = self.session.query(User)
        if kwargs.get('email'):
            email_keyword = '%{}%'.format(kwargs.get('email'))
            query = query.filter(User.email.ilike(email_keyword))

        if kwargs.get('name'):
            name_keyword = '%{}%'.format(kwargs.get('name'))
            query = query.filter(User.name.ilike(name_keyword))

        if kwargs.get('status'):
            query = query.filter(User.status == kwargs.get('status'))

        total = query.count()

        query = query.order_by(User.id.desc())
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return total, query.all()
