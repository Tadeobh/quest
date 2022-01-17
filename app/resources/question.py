from flask_restx import Resource
from flask import request
from marshmallow.utils import pprint
import json

from app.security import token_required
from app.schemas.question_schema import QuestionSchema
from app.db import create_question, delete_question, get_question
from app.common.util import CustomEncoder

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
            return json.loads(CustomEncoder().encode(question))

        else:
            return {'message': "The Question with the given ID does not exist."}, 400

        
    @token_required
    def delete(self, question_id):
        # TODO Delete question.

        # Send the request to delete the Question with the given ID.
        result = delete_question(question_id)

        # If the result is acknowledged and successful, return a success message.
        # If not successful/acknowledged, return a fail message.
        if result.acknowledged and result.deleted_count == 1:

            print('Raw result:')
            pprint(result.raw_result)

            return {'message': "The Question was successfully deleted.",
                    'id': question_id}

        else:
            return {'message': "The Question with the given ID could not be deleted."}