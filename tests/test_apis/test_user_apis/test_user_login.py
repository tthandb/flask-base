import time
import pytest
import json
from test_apis.base import BaseAPITest
from common.helpers.dict_ultility import to_dict
from common.helpers.password import hash_password


ENDPOINT = '/api/v1/services/auth'


class TestUserLogin(BaseAPITest):
    @classmethod
    def setup_class(cls):
        from factories.user import UserFactory

        super().setup_class()
        session = cls.session_factory()
        cls.user_password = hash_password('12345678')

        active_user = UserFactory.create(
            email='{}@example.com'.format(time.time()),
            status='ACTIVE',
            password=cls.user_password
        )
        session.refresh(active_user)
        cls.user_info = to_dict(active_user)

    def send_request(self, login_data):
        return self.client.post(
            ENDPOINT,
            data=json.dumps(login_data)
        )

    def test_login_when_email_missing(self, my_setup):
        response = self.send_request({'password': '12345678'})
        assert response.status_code == 400

    def test_login_when_password_missing(self, my_setup):
        response = self.send_request({'email': self.user_info['email']})
        assert response.status_code == 400

    def test_login_when_password_too_short(self, my_setup):
        response = self.send_request({
            'email': self.user_info['email'],
            'password': 'short'
        })
        assert response.status_code == 400

    def test_login_when_email_wrong(self, my_setup):
        response = self.send_request({
            'email': 'wrong@wrong.com',
            'password': '12345678'
        })
        assert response.status_code == 401

    def test_login_when_password_wrong(self, my_setup):
        response = self.send_request({
            'email': self.user_info['email'],
            'password': '123456789'
        })
        assert response.status_code == 401

    @pytest.mark.parametrize(
        'invalid_status', ['BANED']
    )
    def test_when_user_not_active(self, my_setup, invalid_status):
        from factories.user import UserFactory

        email = '{}@example.com'.format(time.time())
        UserFactory.create(
            email=email,
            status=invalid_status,
            password=self.user_password
        )

        response = self.send_request({
            'email': email,
            'password': '12345678'
        })
        assert response.status_code == 401

    def test_login_success(self, my_setup):
        response = self.send_request({
            'email': self.user_info['email'],
            'password': '12345678'
        })
        assert response.status_code == 200
        assert response.json['token'] is not None
        assert response.json['data']['id'] == self.user_info['id']
        assert 'password' not in response.json['data']
