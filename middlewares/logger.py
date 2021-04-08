import os
import logging
import json
from common.helpers.dict_ultility import to_dict

if not os.path.isdir('./logs'):
    os.mkdir('./logs')

fh = logging.FileHandler(filename='logs/ucellas.log')
logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def write_log(raw_message, level='info', extra=None):
    if extra is None:
        extra = {}

    is_production = True
    message = raw_message
    try:
        extra['message'] = str(message)

        if is_production:
            getattr(logger, level)(json.dumps(to_dict(extra)))
        else:
            getattr(logging, level)(message)
    except Exception:
        logging.error(json.dumps({'message': 'write log failed'}))
