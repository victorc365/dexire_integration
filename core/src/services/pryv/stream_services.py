from pydantic import BaseModel, ConfigDict, Field


class Stream(BaseModel):
    id: str
    name: str
    parent_id: str = Field(alias='parentId')
    client_data: dict = Field(alias='clientData')
    children: list
    trashed: bool
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


class StreamServices:
    pass
