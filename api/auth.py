from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from schemas.user import UserRegisterSchema, UserLoginSchema, RefreshSchema, TokenSchema
from services import auth_service

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
refresh_schema = RefreshSchema()
token_schema = TokenSchema()


class RegisterResource(Resource):
    def post(self):
        """Register a new user
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/UserRegister'
        responses:
          201:
            description: User registered
            schema:
              $ref: '#/definitions/Token'
          400:
            description: Validation error
          409:
            description: Username already exists
        """
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data"}, 400

        try:
            data = register_schema.load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        result = auth_service.register(data["username"], data["password"])
        if not result:
            return {"message": "Username already exists"}, 409

        return token_schema.dump(result), 201


class LoginResource(Resource):
    def post(self):
        """Login
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/UserLogin'
        responses:
          200:
            description: Login successful
            schema:
              $ref: '#/definitions/Token'
          401:
            description: Invalid credentials
        """
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data"}, 400

        try:
            data = login_schema.load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        result = auth_service.login(data["username"], data["password"])
        if not result:
            return {"message": "Invalid credentials"}, 401

        return token_schema.dump(result), 200


class RefreshResource(Resource):
    def post(self):
        """Refresh access token
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/Refresh'
        responses:
          200:
            description: Token refreshed
            schema:
              $ref: '#/definitions/Token'
          401:
            description: Invalid refresh token
        """
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data"}, 400

        try:
            data = refresh_schema.load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        result = auth_service.refresh(data["refresh_token"])
        if not result:
            return {"message": "Invalid or expired refresh token"}, 401

        return token_schema.dump(result), 200