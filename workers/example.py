import os
import time
import math
import csv
import shutil
import pytz
import base64
from .base_worker import BaseWorker, connect_database
from database.session import session_scope

class ExampleWorker(BaseWorker):
    @connect_database
    def run(self, message):
        print("Example Worker")
        print(message)