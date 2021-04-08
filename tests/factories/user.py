import time
import factory
from .base import UModelFactory
from database.models.user import User


class ShopFactory(UModelFactory):
    class Meta:
        model = User

    name = factory.Faker('name')
