from marshmallow import Schema, fields
from marshmallow.validate import Length

class AnswerSchema(Schema):
    # Answer ID
    _id = fields.String(validate=Length(equal=24))

    # Question ID
    question_id = fields.String(required=True, validate=Length(equal=24))

    # Value (Can be any type as needed)
    value = fields.Raw(required=True)