from flask_restx import Resource
from flask import request

from app.security import token_required
from app.schemas.answer_schema import AnswerSchema
from app.db import create_answer, get_answer

class Answer(Resource):
    # Create a AnswerSchema() instance to validate the info
    answer_schema = AnswerSchema()

    @token_required
    def post(self):
        # Get the information through the request
        request_data = request.json

        # Validate the information
        validated_data = Answer.answer_schema.load(request_data)

        # Save the new answer in the database
        result = create_answer(**validated_data)

        # If the insertion has been acknowledged by the database and an ID
        # has been created for the new answer, return a success message.
        if type(result) is not dict and type(result) is not None:
            if result.acknowledged is True and result.inserted_id is not None:
                return {'message': "Answer created successfully.",
                        'id': str(result.inserted_id)
                        }, 201

            else:
                return {'message': "An error happened while saving the new answer in the database."}, 400
        
        else:
            return result, 404


    @token_required
    def get(self, answer_id):
        # TODO Get answer and check if it belongs to the user
        # before sending it back to the them.

        # Check if the questionnaire with the given ID exists.
        answer = get_answer(answer_id)

        if answer is not None:
            return {

                '_id': str(answer.get('_id')),
                'question_id': str(answer.get('question_id')),
                'value': answer.get('value')
            }

        else:
            return {'message': "The Answer with the given ID does not exist."}, 400