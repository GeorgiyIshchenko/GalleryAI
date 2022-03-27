import json
from marshmallow import Schema, fields


class Photo_Schema(Schema):
    id = fields.Int()
    tag = fields.Str()
    image = fields.Str()
    description = fields.Str()
    status = fields.Str()
    created_at = fields.Str()
    is_ai_tag = fields.Bool()
    user = fields.Int()
    '''
    def __init__(self, id, tag, image, description, status, created_at, is_ai_tag, user):
        self.id = id
        self.tag = tag
        self.image = image
        self.description = description
        self.status = status
        self.created_at = created_at
        self.is_ai_tag = is_ai_tag
        self.user = user
    '''


class Dict2Photo(object):

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
