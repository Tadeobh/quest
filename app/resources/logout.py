from datetime import datetime, timedelta
from importlib.resources import Resource
from flask import make_response, request


from flask_restx import Resource
from app.db import get_user_with_rt, sign_out_session

from app.resources.refresh import Refresh

class Logout(Resource):

    def get(self):
         # Get the Refresh Token from the request
        refresh_token = request.cookies.get('jwt')

        # If the Refresh Token does not exist, return 'No Content' success status
        if refresh_token is None:
            return make_response('', 204)
        
        # If the Refresh Token exists, check if it is an active session
        user = get_user_with_rt(refresh_token)
        
        # If a user was found with the Refresh Token, delete the session from the db
        if user is not None:
            sign_out_session(user.get('username'), refresh_token)

        # Create a new response
        log_out_response = make_response('', 204)

        # Clear the Refresh Token cookie
        log_out_response.set_cookie(
            'jwt',
            '',
            expires=(datetime.today() - timedelta(seconds=1.0)), httponly=True)
        
        # Return the response
        return log_out_response