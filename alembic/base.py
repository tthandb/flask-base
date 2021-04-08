import os
import sys
from functools import wraps
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
# from bin.automodel import build_model # noqa


def auto_build_model(table_name, action='create'):
    def build_model_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # if os.getenv('ENVIRONMENT') in ['develop']:
            #     build_model(table_name, action=action)
            return result

        return func_wrapper

    return build_model_decorator
