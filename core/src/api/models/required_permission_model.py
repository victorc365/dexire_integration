from api.models.abstract_model import AbstractModel
from pydantic import ConfigDict, Field


class RequiredPermissionModel(AbstractModel):
    stream_id: str = Field(description='The id of the stream for which the permission is requested',
                           alias='streamId')
    level: str = Field(
        description='The permission required. Value can be contribute/read/manage')
    default_name: str = Field(description='Default name of the stream. This is the name showed to the user',
                              alias='defaultName')
    model_config = ConfigDict(json_schema_extra={
        'stream_id': 'devBot_heartbeat',
        'level': 'manage',
        'default_name': 'heartbeat',
    })