from common.api import UResource


class Example(UResource):
    def get(self):
        return {'message': 'test_success'}
