from flask_restx import Resource
from flask import request

from app.security import token_required
from app.schemas.question_schema import QuestionSchema
from app.db import create_question

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
