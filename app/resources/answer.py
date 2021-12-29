from flask_restx import Resource
from flask import request

from app.security import token_required
from app.schemas.answer_schema import AnswerSchema
from app.db import create_answer

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