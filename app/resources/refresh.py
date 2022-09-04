from datetime import datetime, timedelta
from flask import current_app, make_response, request
from flask_restx import Resource
import jwt

from app.db import add_session, get_user_with_rt, sign_out_all, sign_out_session

class Refresh(Resource):

    def get(self):

        # Get the cookie with the refresh token.
        refresh_token = request.cookies.get('jwt')

        # If there isn't a refresh token in the cookies, return an error.
        if refresh_token is None:
            return {'message': 'Refresh Token not found. Please try again.'}, 401

        # Get the user from the Refresh Token.
        found_user = get_user_with_rt(refresh_token)

        # If a user was not found, this a reused refresh token.
        if found_user is None:   
            try:
                # Get the username from the refresh token
                decoded_info = jwt.decode(refresh_token, current_app.config['REFRESH_TOKEN_KEY'], algorithms="HS256")

                # Delete all the active sessions from the user
                sign_out_all(decoded_info['username'])

                # Create a new response with 403 status
                new_response = make_response(
                    {
                        'message': 'Invalid refresh token. Please try again.',
                        'debug': 'Refresh Token Reuse. Deleted all sessions from db.'
                    }, 403)
                
                # Clear the cookie session
                new_response.set_cookie('jwt', value='', expires=datetime(1970, 1, 1), httponly=True)

                # Return the response with the cookie cleared out
                return new_response

            # If the refresh token is expired, return a 403 status
            except jwt.ExpiredSignatureError:
                return {
                        'message': 'Invalid refresh token. Please try again.',
                        'debug': 'Refresh Token Reuse. Expired Refresh Token.'
                    }, 403                 

        try:
            # Decode the token using the applications Secret Key.
            data = jwt.decode(refresh_token, current_app.config['REFRESH_TOKEN_KEY'], algorithms="HS256")

            # Retrieve the username from the token.
            decoded_username = data.get('username')

        except jwt.ExpiredSignatureError:
            # Refresh token is invalid so it needs to be removed from the db
            sign_out_session(found_user.get('username'), refresh_token)

            # Create a new response with the error message and status 403
            expired_rt_response = make_response(
                {
                    'message': 'Invalid refresh token. Please try again.',
                    'debug': 'Refresh Token NOT Reused. Expired Refresh Token'
                }, 403
            )

            # Clear the session cookie from the response
            expired_rt_response.set_cookie('jwt', value='', expires=datetime(1970, 1, 1), httponly=True)

            # Return an error message.
            return expired_rt_response

        if found_user.get('username') != decoded_username:
            # If the decoded username and the user found in the database are not the same,
            # return an error.
            return {'message': 'Invalid user.'}, 403
        
        # Delete the existing (used) refresh token from the db
        sign_out_session(found_user.get('username'), refresh_token)

        print('[Creating New Session]')

        # Create a new refresh token for the user
        new_session = jwt.encode(
            {
                'username': found_user.get('username'),
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            current_app.config['REFRESH_TOKEN_KEY'],
            algorithm="HS256"
        )
        
        # Save the session in the db
        add_session(found_user.get('username'), new_session)

        # Generate a new access token
        access_token = jwt.encode(
            {
                'username': decoded_username,
                'exp': datetime.utcnow() + timedelta(minutes=15)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        # Create a response with the new Access Token
        tokens_response = make_response({
            'accessToken': access_token,
            'username': found_user.get('username'),
            'user_id': str(found_user.get('_id'))
            }, 200)

        # Add the refresh token to the response
        tokens_response.set_cookie('jwt', value=new_session, httponly=True, max_age=24 * 60 * 60 * 1000)

        # Return the new access and refresh tokens generated
        return tokens_response