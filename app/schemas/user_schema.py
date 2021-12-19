from marshmallow import Schema, fields
from marshmallow.decorators import pre_load
from marshmallow.utils import EXCLUDE
from marshmallow.validate import Length

class RegisterUserSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    email = fields.Email(Required=True)
    password = fields.Str(required=True)

    class Meta:
        uknown = EXCLUDE

class LogUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

    class Meta:
        uknown = EXCLUDE

    @pre_load
    def email_as_username(self, data, **kwargs):
        # If the user sent an 'email' instead of a username
        # use it as 'username'.
        if data.get('email'):
            data['username'] = data.get('email')
        return data