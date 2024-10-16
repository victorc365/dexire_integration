from peewee import *
import datetime
import json
import pathlib
import os

db: SqliteDatabase = SqliteDatabase(str(pathlib.Path(__file__).parent / 'logs.sqlite3'))
    
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
        
# save the recommendation query
class RecommendationQuery(BaseModel):
    id = AutoField()
    agent_id = CharField()
    json_query = JSONField()
    query_date = DateTimeField(default=datetime.datetime.now)
    recommendation_type = CharField()
    
class AnswerQuery(BaseModel):
    id = AutoField()
    answer = JSONField()
    answer_date = DateTimeField(default=datetime.datetime.now)
    query = ForeignKeyField(RecommendationQuery, backref='answer_query')
    
class UserFeedback(BaseModel):
    id = AutoField()
    answer = ForeignKeyField(AnswerQuery, backref='user_feedback')
    feedback_type = CharField()
    feedback = JSONField()

class UserSpecificationLogs(BaseModel):
    uuid = CharField()
    user_data = JSONField(null=True)

class OfferRoundLogs(BaseModel):
    uuid = CharField()
    action = CharField()
    explanation = CharField()
    recipe_info = JSONField()
    time_stamp = DateTimeField(default=datetime.datetime.now)

class FeedbackLogs(BaseModel):
    uuid = CharField()
    offer_id = ForeignKeyField(model=OfferRoundLogs)
    feedback_type = CharField()
    feedback = CharField()

class RoundSummary(BaseModel):
    uuid = CharField()
    total_offers = IntegerField()
    is_terminated = BooleanField()


if not os.path.exists(str(pathlib.Path(__file__).parent / 'logs.sqlite3')):
    db.create_tables([RecommendationQuery, AnswerQuery, UserFeedback])

if __name__ == "__main__":
    db.create_tables([RecommendationQuery, AnswerQuery, UserFeedback])