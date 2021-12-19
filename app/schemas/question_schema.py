from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf

class OptionSchema(Schema):
    value = fields.String(required=True, validate=Length(max=255))

class QuestionSchema(Schema):
    # Question ID
    _id = fields.String(validate=Length(equal=24))

    # Questionnaire ID
    questionnaire_id = fields.String(required=True)

    # Text of the question
    text = fields.String(required=True, validate=Length(min=3, max=255))

    # Type of question: text, email, list, one_of, many_of, int_number, float_number
    type = fields.String(required=True, validate=OneOf(['text', 'email', 'list', 'one_of', 'many_of', 'int', 'float']))

    # Options (Not required. Only for list, one_of, many_of)
    options = fields.List(fields.String(validate=Length(min=1, max=255)))