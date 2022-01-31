from flask import current_app, request
import datetime
from flask_restx import Resource
from werkzeug.security import check_password_hash
import jwt

from app.db import get_user

from app.schemas.user_schema import LogUserSchema

class Auth(Resource):
    # Create an instance of UserSchema() to validate the info
    login_schema = LogUserSchema()

    def post(self):

        # Get the information sent through the request
        json_data = request.json

        # Validate the information
        data = Auth.login_schema.load(json_data)

        # Get the user with the given username and/or email.
        user = get_user(email=data.get('email', None), username=data.get('username', None))

         # If the given password matches the given user's password,
         # send back the JWToken.
        if check_password_hash(user.get('password'), data.get('password')):
            
            # Encode the token using the application's Secret Key
            # with the username and expiration in the payload.
            token = jwt.encode(
                {
                'username': user.get('username'),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                current_app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            # Return the token to the user.
            return {'access_token': token}
        
        # Return an error message if the user could not be authenticated.
        return {'message': 'Could not verify user.'}, 404
