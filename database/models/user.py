import os
from enum import Enum
from sqlalchemy import Column, INTEGER, BOOLEAN, VARCHAR, JSON, FLOAT
from database.models.base import DeclarativeBase, Base, DateTimestamp
from common.helpers.dict_ultility import to_dict


class UserStatus(Enum):
    ACTIVE = 'ACTIVE'
    BANED = 'BANED'


class User(DeclarativeBase, Base, DateTimestamp):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR, nullable=True, default=None)
    email = Column(VARCHAR, nullable=True, default=None)
    password = Column(VARCHAR, nullable=True, default=None)
    status = Column(VARCHAR, nullable=True, default=None)
    tokens = Column(JSON, nullable=True, default=None)
    timezone = Column(FLOAT, nullable=True, default=-8)
    address = Column(VARCHAR, nullable=True, default=None)
    phone = Column(VARCHAR, nullable=True, default=None)
    city = Column(VARCHAR, nullable=True, default=None)
    zipcode = Column(VARCHAR, nullable=True, default=None)
    country = Column(VARCHAR, nullable=True, default=None)
    country = Column(VARCHAR, nullable=True, default=None)
    first_name = Column(VARCHAR, nullable=True, default=None)
    last_name = Column(VARCHAR, nullable=True, default=None)
    configs = Column(JSON, nullable=True, default=None)

    def to_json(self):
        return to_dict(self)

    def to_json_except_keys(self):
        obj = to_dict(self)
        for key in self.except_keys():
            if key in obj:
                del obj[key]
        return obj

    def except_keys(self):
        return {
            'password',
            'tokens'
        }
