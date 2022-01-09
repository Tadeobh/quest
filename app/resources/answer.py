from flask_restx import Resource
from flask import request
from marshmallow.utils import pprint

from app.security import token_required
from app.schemas.answer_schema import AnswerSchema
from app.db import create_answer, delete_answer, get_answer, delete_answer

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
    

    @token_required
    def delete(self, answer_id):
        # TODO Delete Answer.

        # Send the request to delete the Answer with the given ID.
        result = delete_answer(answer_id)

        # If the result is acknowledged and successful, return a success message.
        # If not successful/acknowledged, return a fail message.
        if result.acknowledged and result.deleted_count == 1:
            return {'message': "The Answer was successfully deleted.",
                    'id': answer_id}

        else:
            return {'message': "The Answer with the given ID could not be deleted."}