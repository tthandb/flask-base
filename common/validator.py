import re
from marshmallow import ValidationError, Schema, fields, utils
from flask import request as flask_request
from flask_restful import request
from functools import wraps


NOT_EMPTY_REGEX = r'^(?!\s*$).+'
DOMAIN_REGEX = r'^[a-zA-z0-9\-]'
CODE_REGEX = r'^[a-zA-z0-9\-\_]'
CELLA_CODE_REGEX = r'^[0-9]'
EMAIL_REGEX = r'^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+'


class USchema(Schema):
    def all_or_none_of(self, data, *keys):
        if all(key in data for key in keys):
            return
        if all(key not in data for key in keys):
            return
        raise ValidationError(
            'All of {} must be existed or not in the same time'.format(keys)
        )

    def exactly_one_of(self, data, *keys):
        if sum(key in data for key in keys) != 1:
            raise ValidationError(
                'Only one of {} must be provided'.format(keys))

    def nothing_or_one_of(self, data, *keys):
        sum_key = sum(key in data for key in keys)
        if sum_key not in [0, 1]:
            raise ValidationError(
                'Nothing or one of {} must be provided'.format(keys))

    def at_least_one_of(self, data, *keys):
        if any(key in data for key in keys):
            return
        raise ValidationError(
            'At least one of {} must be existed'.format(keys)
        )

    def cast_num_to_str(self, data, *keys):
        for key in keys:
            if key in data and isinstance(data[key], (int, float)):
                data[key] = str(data[key])
        return data


class UParamList(fields.List):
    def _deserialize(self, value, attr, data, **kwargs):
        if not utils.is_collection(value):
            value = [value]
        return super(UParamList, self)._deserialize(
            value, attr, data, **kwargs)


def validate_body(validate_schema, many=False):
    def is_form(content_type):
        return (
            ('application/x-www-form-urlencoded' in content_type) or
            ('multipart/form-data' in content_type)
        )

    def validate_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            content_type = request.headers.get('Content-Type', '')

            if is_form(content_type):
                data = validate_schema().load(request.form)
                args[0].body = data
            else:
                json_data = request.get_json(force=True)
                data = validate_schema(many=many).load(json_data)
                args[0].body = data

            return func(*args, **kwargs)

        return func_wrapper

    return validate_decorator


def validate_params(validate_schema):
    def validate_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            params = request.args.to_dict()
            param_keys = list(params.keys())
            nested_regex = re.compile(r'\w+(\[\w+\])+')
            for key in param_keys:
                if key[-2:] == '[]':
                    params[key[:-2]] = flask_request.args.getlist(key)
                    del params[key]
                    continue
                if nested_regex.match(key):
                    value = params.pop(key, None)
                    params = merge_nested_params(params, key, value)
                    continue
            data = validate_schema().load(params)
            args[0].query = data

            return func(*args, **kwargs)

        return func_wrapper

    return validate_decorator


def parse_nested_params(key, value):
    '''
    key will have format a[b][c][d]
    '''
    elements = key.split('[')
    number_elements = len(elements)

    nested_param = {}
    nested_keys = []
    handling_params = nested_param
    for index, element in enumerate(elements):
        if element[-1] == ']':
            element = element[:-1]
        nested_keys.append(element)
        if index == number_elements - 1:
            handling_params[element] = value
            continue
        nested_param[element] = handling_params = {}

    return nested_keys, nested_param


def merge_nested_params(params, key, value):
    '''
    key will have format a[b][c][d]
    '''
    nested_keys, nested_param = parse_nested_params(key, value)

    handling_params = params
    handling_nested = nested_param
    for nested_key in nested_keys:
        handling_nested = handling_nested[nested_key]
        if nested_key not in handling_params:
            handling_params[nested_key] = handling_nested
            break
        handling_params = handling_params[nested_key]
        if not isinstance(handling_params, dict):
            break

    return params
