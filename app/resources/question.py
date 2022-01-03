from flask_restx import Resource
from flask import request

from app.security import token_required
from app.schemas.question_schema import QuestionSchema
from app.db import create_question, get_question

class Question(Resource):
    # Create a QuestionSchema() instance to validate the info
    question_schema = QuestionSchema()

    @token_required
    def post(self):
        # Get the information through the request
        request_data = request.json

        # Validate the information
        validated_data = Question.question_schema.load(request_data)

        # Save the new question in the database
        result = create_question(**validated_data)

        # If the insertion has been acknowledged by the database and an ID
        # has been created for the new question, return a success message.
        if type(result) is not dict and type(result) is not None:
            if result.acknowledged is True and result.inserted_id is not None:
                return {'message': "Question created successfully.",
                        'id': str(result.inserted_id)
                        }, 201

            else:
                return {'message': "An error happened while saving the new question in the database."}, 400
        
        else:
            return result, 404


    @token_required
    def get(self, question_id):
        # TODO Get questionnaire and check if it belongs to the user
        # before sending it back to the them.

        # Check if the questionnaire with the given ID exists.
        question = get_question(question_id)

        if question is not None:
            result = {

                '_id': str(question.get('_id')),
                'questionnaire_id': str(question.get('questionnaire_id')),
                'text': question.get('text'),
                'type': question.get('type')
            }

            if question.get('options'):
                result['options'] = question.get('options')

            return result

        else:
            return {'message': "The Questionnaire with the given ID does not exist."}, 400