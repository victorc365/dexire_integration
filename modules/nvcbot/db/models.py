from peewee import *
import datetime
import json

db = SqliteDatabase('logs.sqlite3')

class JSONField(TextField):
    def db_value(self, value):
        # serialize JSON to string
        return value if value is None else json.dumps(value)

    def python_value(self, value):
        # deserialize
        return value if value is None else json.loads(value)

class BaseModel(Model):
    class Meta:
        database = db

class UserSpecificationLogs(BaseModel):
    uuid = CharField()
    user_data = JSONField(null=True)

class OfferRoundLogs(BaseModel):
    uuid = CharField()
    is_accepted = BooleanField()
    explanation = CharField()
    recipe_info = JSONField()

class FeedbackLogs(BaseModel):
    uuid = CharField()
    offer_id = ForeignKeyField(model=OfferRoundLogs)
    feedback_type = CharField()
    feedback = CharField()

class RoundSummary(BaseModel):
    uuid = CharField()
    total_offers = IntegerField()
    is_terminated = BooleanField()