from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True, validate=validate.Length(min=6))


class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()


class RefreshSchema(Schema):
    refresh_token = fields.Str(required=True)