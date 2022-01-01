from flask_restx import Resource
from flask import request, g

from app.schemas.questionnaire_schema import QuestionnaireSchema
from app.db import create_questionnaire, get_questionnaire
from app.security import token_required

class Questionnaire(Resource):
    # TODO Create the Schema instance for the Questionnaire resource.

    # Create an instance of UserSchema() to validate the info
    quest_schema = QuestionnaireSchema()

    @token_required
    def post(self):
        # Get the information sent through the request
        request_data = request.json

        # Add the username to the data
        request_data['user_id'] = g._current_user.get('username')

        # Validate the information
        validated_data = Questionnaire.quest_schema.load(request_data)

        # Save the new questionnaire in the database
        result = create_questionnaire(**validated_data)

        # If the insertion has been acknowledged by the database and an ID
        # has been created for the new questionnaire, return a success message.
        if result.acknowledged is True and result.inserted_id is not None:
            return {'message': "Questionnaire created successfully.",
                    'id': str(result.inserted_id)
                    }, 201
        else:
            return {'message': "An error happened while saving the new questionnaire in the database."}, 400

    
    @token_required
    def get(self, questner_id):
        # TODO Get questionnaire and check if it belongs to the user
        # before sending it back to the them.

        # Check if the questionnaire with the given ID exists.
        questionnaire = get_questionnaire(questner_id)

        if questionnaire is not None:
            return {

                '_id': str(questionnaire.get('_id')),
                'title': questionnaire.get('title'),
                'user_id': questionnaire.get('user_id')
            }

        else:
            return {'message': "The Questionnaire with the given ID does not exist."}, 400