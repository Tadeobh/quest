from flask import current_app, make_response, request
from datetime import datetime, timedelta
from flask_restx import Resource
from werkzeug.security import check_password_hash
import jwt

from app.db import add_session, get_user, get_user_with_rt, sign_out_all, sign_out_session

from app.schemas.user_schema import LogUserSchema

class Auth(Resource):

    # Create an instance of UserSchema() to validate the info
    login_schema = LogUserSchema()

    def post(self):

        # Get the information sent through the request
        json_data = request.json

        # Validate the information
        data = Auth.login_schema.load(json_data)

        # Retrieve the Refresh Token, if any
        refresh_token = request.cookies.get('jwt')

        # Check if there is a Refresh Token
        if refresh_token is not None:
            
            # Check if there is a user with the Refresh Token
            found_user = get_user_with_rt(refresh_token)

            # If there is not a user, then this Refresh Token is being reused
            if found_user is None:

                # Sign out from all sessions
                sign_out_all(data.get('username'))
                
                # Create a new response with an 'Unauthorized' error
                unautorized_response = make_response(
                    {'message': 'Unauthorized log in.'}, 403
                )

                # Clear the Refresh Token cookie in the new response
                unautorized_response.set_cookie(
                    'jwt',
                    '',
                    expires=datetime(1970, 1, 1), httponly=True)

                # Return response
                return unautorized_response
            
            print('[Found User]: {}'.format(found_user.get('username')))

            # Remove session from the found user
            sign_out_session(found_user.get('username'), refresh_token)

        # Get the user with the given username and/or email.
        user = get_user(email=data.get('email', None), username=data.get('username', None))

        # Return an error message if the user could not be authenticated.
        if user is None:
            return {'message': 'Wrong user and/or password.'}, 401

         # If the given password matches the given user's password,
         # send back the JWToken.
        if check_password_hash(user.get('password'), data.get('password')):
            
            # Encode the Access Token using the application's Secret Key
            # with the username and expiration in the payload.
            access_token = jwt.encode(
                {
                    'username': user.get('username'),
                    'exp': datetime.utcnow() + timedelta(seconds=10)
                },
                current_app.config['SECRET_KEY'],
                algorithm="HS256"
            )
            
            # Encode the Refresh Token using the application's Secret Key
            # with the username and expiration in the payload.
            new_refresh_token = jwt.encode(
                {
                'username': user.get('username'),
                'exp': datetime.utcnow() + timedelta(minutes=1)
                },
                current_app.config['REFRESH_TOKEN_KEY'],
                algorithm="HS256"
            )
            
            # Create a response with the user_id and accessToken that will be
            # available for the frontend JavaScript.
            response = make_response(
                {
                    'user_id': str(user.get('_id')),
                    'accessToken': access_token
                }, 200
            )

            # Add to the response an httpOnly cookie with the Refresh Token that 
            # will not be accessible through JavaScript.
            response.set_cookie('jwt', value=new_refresh_token, httponly=True, max_age=24 * 60 * 60 * 1000)

            print('[New Refresh Token]: {}'.format(new_refresh_token))

            # Add the Refresh Token to the user's Refresh Token list
            add_session_result = add_session(username=user.get('username'), refresh_token=new_refresh_token)

            # Confirm the Refresh Token was saved
            if add_session_result is None or add_session_result.modified_count != 1:
                return {
                    'message': 'Server could not save the session. Please try logging in again'}, 500

            # Return the response to the client.
            return response
        
        # TODO: Get rid of this "elif" statement with a general Response
        elif refresh_token is not None:
            # Create an error response if the user could not be authenticated and provided a 
            # session
            error_response = make_response(
                {'message': 'Wrong user and/or password (cookie).'}, 401
            )

            # Clear the Refresh Token cookie in the new response
            error_response.set_cookie(
                'jwt',
                '',
                expires=datetime(1970, 1, 1), httponly=True)

            # Return the response
            return error_response

        else:
            # Return an error message if the user could not be authenticated.
            return {'message': 'Wrong user and/or password.'}, 401
