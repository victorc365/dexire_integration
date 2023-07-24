from api.models.abstract_model import AbstractModel
from pydantic import ConfigDict, Field


class BotModel(AbstractModel):
    name: str = Field(description='Name of the Bot')
    url: str = Field(description='Url of the server serving the bot')
    is_dev: bool = Field(
        description='Indicate wether the bot is still under development or not',
        alias='isDev')
    model_config = ConfigDict(json_schema_extra={
        'name': 'DevBot',
        'url': 'http://my-url.com',
        'isDev': True,
    })
