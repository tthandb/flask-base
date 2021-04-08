from marshmallow import fields, validates_schema, EXCLUDE
from marshmallow.validate import Regexp, OneOf, Range, Length
from common.validator import USchema, UParamList, NOT_EMPTY_REGEX


class RequestLoginSchema(USchema):

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


class RequestSignUpSchema(USchema):
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
