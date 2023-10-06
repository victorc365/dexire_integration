from typing import List

from api.models.abstract_model import AbstractModel
from api.models.required_permission_model import RequiredPermissionModel
from pydantic import ConfigDict, Field


class BotModel(AbstractModel):
    name: str = Field(description='Name of the Bot')
    description: str = Field(description='A description of the bot')
    url: str = Field(description='Url of the server serving the bot')
    is_dev: bool = Field(
        description='Indicate whether the bot is still under development or not',
        alias='isDev')
    is_pryv_required: bool = Field(
        description='Indicate weather the bot is using pryv as database.',
        alias='isPryvRequired'
    )
    required_permissions: List[RequiredPermissionModel] = Field(
        description='',
        alias='requiredPermissions'
    )
    model_config = ConfigDict(json_schema_extra={
        'name': 'DevBot',
        'url': 'https://my-url.com',
        'isDev': True,
        'isPryvRequired': True,
        'required_permissions': [
            {
                'streamId': 'devBot_stream',
                'level': 'manage',
                'defaultName': 'stream'
            }
        ]
    })