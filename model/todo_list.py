#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel
import jsonschema


class TodoList(BaseModel):
    def validate_items(prop, value):
        if value is not None:
            schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "completed": {"type": "boolean"},
                        "description": {"type": "string"}
                    }
                }
            }
            jsonschema.validate(value, schema)

    name = ndb.StringProperty(required=True, indexed=False)
    items = ndb.JsonProperty(indexed=False, validator=validate_items)
    users = ndb.KeyProperty(kind='User', repeated=True)
