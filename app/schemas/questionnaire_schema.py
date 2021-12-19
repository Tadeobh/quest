from marshmallow import Schema, fields
from marshmallow.validate import Equal, Length

from app.schemas.question_schema import QuestionSchema

class QuestionnaireSchema(Schema):
    # Questionnaire ID
    _id = fields.String(validate=Length(equal=24))

    # Title of the questionnaire
    title = fields.String(required=True, validate=Length(min=3, max=255))
    
    # User ID
    user_id = fields.String(required=True)
    
    # List of questions
    questions = fields.List(fields.Nested(QuestionSchema(only=('_id',))))