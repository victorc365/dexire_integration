from pydantic import BaseModel, ConfigDict, Field


class Attachment(BaseModel):
    id: str
    file_name: str = Field(alias='fileName')
    type: str
    size: int
    read_token: str = Field(alias='readToken')
    integrity: str
    model_config = ConfigDict(
        # remove whitespaces in the beginning / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instantiate model from attribute of another class
        from_attributes=True,
    )


class Event(BaseModel):
    id: str
    stream_ids: list[str] = Field(alias='streamIds')
    time: float
    duration: float
    type: str
    content: any
    description: str
    attachments: list[Attachment]
    client_data: dict = Field(alias='clientData')
    trashed: bool
    integrity: str
    created: float
    created_by: str = Field(alias='createdBy')
    modified: float
    modified_by: str = Field(alias='modifiedBy')
    model_config = ConfigDict(
        # remove whitespaces in the beginning / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instantiate model from attribute of another class
        from_attributes=True,
    )


class EventServices:
    pass
