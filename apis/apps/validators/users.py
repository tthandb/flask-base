from marshmallow import fields, validates_schema, EXCLUDE
from marshmallow.validate import Regexp, OneOf, Range, Length
from common.validator import USchema, UParamList, NOT_EMPTY_REGEX


class RequestCreateUserSchema(USchema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True,
        allow_none=False
    )

    password = fields.String(
        required=True,
        allow_none=False,
        validate=[Length(min=8)]
    )


class UpdateUser(USchema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=False,
        allow_none=True,
        validate=Regexp(NOT_EMPTY_REGEX)
    )


class RequestUpdateUserSchema(USchema):

    class Meta:
        unknown = EXCLUDE

    user = fields.Nested(
        UpdateUser,
        required=True,
        allow_none=False
    )


class UserFilter(USchema):

    class Meta:
        unknown = EXCLUDE

    page = fields.Integer(
        required=True,
        allow_none=False
    )
    page_size= fields.Integer(
        required=False,
        allow_none=False
    )

    email = fields.String(
        required=False,
        allow_none=False,
        validate=Regexp(NOT_EMPTY_REGEX)
    )