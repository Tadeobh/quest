from flask_restx import Resource
from flask import request

from app.db import create_new_user, user_exists
from app.schemas.user_schema import RegisterUserSchema

class User(Resource):

    # Create an instance of UserSchema() to validate the info
    register_schema = RegisterUserSchema()

    def post(self):
        # Get the information sent through the request
        request_data = request.json

        # Validate the information
        data = User.register_schema.load(request_data)

        # Check if the username or email are already in use.
        email_exists = user_exists(email=data['email'])
        username_exists = user_exists(username=data['username'])
        
        # If the user with the given username or email already exists, return a 409 error
        if username_exists:
            return {'message': "Username '{}' already exists.".format(data['username'])}, 409
        elif email_exists:
            return {'message': "Email '{}' is already taken. Please try with a different email.".format(data['email'])}, 409
        
        # If the user doesn't exist, create it and save it to the database
        result = create_new_user(**data)

        # If the insertion has been acknowledged by the dataabase and an ID
        # has been created for the new user, return a success message.
        if result.acknowledged is True and result.inserted_id is not None:
            return {'message': "User '{}' created successfully.".format(data['username'])}, 201
        else:
            return {'message': "An error happened while saving the new user in the database."}, 400