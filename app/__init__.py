from turtle import end_poly
from flask import Flask
from flask_restx import Api

from app.resources.auth import Auth
from app.resources.logout import Logout
from app.resources.refresh import Refresh
from app.resources.user import User
from app.resources.questionnaire import Questionnaire
from app.resources.question import Question
from app.resources.answer import Answer

def create_app(settings_module):
    """
    Function to create the app based on the given "settings_module".
    """

    # Set the instance_relative_config parameter to True
    # so Flask knows that the directory /instance is at the same same level as the /app directory
    app = Flask(__name__, instance_relative_config=True)

    # Load the configuration from the settings_module file
    app.config.from_object(settings_module)

    # Check if we are in a testing environment or production environment
    if app.config.get('TESTING', False):
        app.config.from_pyfile('config-testing.py', silent=True)
    else:
        app.config.from_pyfile('config.py', silent=True)

    # Initialize the Api object with the app environment
    api = Api(app)

    # Register the API endpoints for individual resources.
    # Authentication resource
    api.add_resource(Auth, '/auth', endpoint='auth')

    # Logout resource to delete the user's session
    api.add_resource(Logout, '/logout', endpoint='logout')

    # Endpoint to refresh the Access Token
    api.add_resource(Refresh, '/refresh', endpoint='refresh')

    # Endpoints to "add" resources.
    api.add_resource(User, '/users', endpoint='add_user')
    api.add_resource(Questionnaire, '/questionnaires', endpoint='add_questionnare')
    api.add_resource(Question, '/questions', endpoint='add_question')
    api.add_resource(Answer, '/answers', endpoint='add_answer')

    # Endpoints to get and delete resources with a given ID.
    api.add_resource(Questionnaire, '/questionnaires/<string:questner_id>', endpoint='questionnaire')
    api.add_resource(Question, '/questions/<string:question_id>', endpoint='question')
    api.add_resource(Answer, '/answers/<string:answer_id>', endpoint='answer')

    # Return app object with all the configuration
    return app