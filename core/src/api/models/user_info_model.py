from api.models.abstract_model import AbstractModel
from pydantic import ConfigDict, Field

class UserInfoModel(AbstractModel):
    token: str = Field(description='The token generated after user gave his consent to access his data')
    username: str = Field(description='The username of the user in order to create bots')
    model_config = ConfigDict(json_schema_extra={
        'token': 'clkvfdksj83fj',
        'username': 'my_username'
    })