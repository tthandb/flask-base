import os
import time
import faktory
from background_jobs import connect_database
from common.helpers.dict_ultility import to_dict
from database.services.user import UserService


class AbandonedCheckouts(object):
    @connect_database
    def run(self):
        self.user_service = UserService(self.session)

