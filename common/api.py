from flask_restful import Api, Resource
import datetime


class UApi(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert_time_int_to_string(self, timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).replace(
            tzinfo=datetime.timezone.utc
        ).isoformat()
