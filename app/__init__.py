from flask import Flask
from flask_restx import Api

from app.resources.auth import Auth
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

    # Register the API endpoints for individual resources
    api.add_resource(Auth, '/auth', endpoint='auth')
    api.add_resource(User, '/users', endpoint='users')
    api.add_resource(Questionnaire, '/questionnaires', endpoint='questionnares')
    api.add_resource(Question, '/questions', endpoint='questions')
    #api.add_resource(Answer, '/answers', endpoint='answer')

    # Register the API endpoints for list of resources 
    # associated to a single parent resource
    #api.add_resource(UserQuestionnaires, '/users/<str:username>/questionnaires', endpoint='user_questionnaires')
    #api.add_resource(QuestQuestions, '/questionnaires/<id:questionnaire_id>/questions', endpoint='quest_questions')
    #api.add_resource(QuestionAnswers, '/questions/<id:question>/answers', endpoint='question_answers')

    # Return app object with all the configuration
    return app