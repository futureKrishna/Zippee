from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    role = fields.Str()

from marshmallow import Schema, fields, INCLUDE

class TaskSchema(Schema):
    class Meta:
        unknown = INCLUDE
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    completed = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    user_id = fields.Int()
