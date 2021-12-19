from flask import request, current_app, g
import jwt
from functools import wraps
from functools import wraps

from app.db import get_user


def token_required(f):
    """
    Decorator to validate the user's JSON Web Token.
    """

    @wraps(f)
    def decorator(*args, **kwargs):

        # Initialize the token with no value assigned to it.
        token = None

        # Check if we have an authorization value in the headers from the request.
        if 'authorization' in request.headers:

            # Get the JSON Web Token from the "Authorization" header.
            token = request.headers['authorization']

        # If the token does not have a value, return an error.
        if not token:
            return {'message': 'a valid token is missing'}, 404

        try:
            # Decode the token using the applications Secret Key.
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")

            # Store the username on Flask's global variable.
            g._current_user = get_user(username=data['username'])

        except Exception as e:
            # Return an error message if the token is invalid.
            return {'message': 'invalid token', 'token': token}, 404

        return f(*args, **kwargs)
    
    return decorator