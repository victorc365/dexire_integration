from pydantic import BaseModel, ConfigDict


class AbstractModel(BaseModel):
    '''
        This model is used to set general configuration for
        pydantic models. All models have to extend this instead of BaseModel
    '''
    model_config = ConfigDict(
        # remove whitespaces in the beggining / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instanciate model from attribute of another class
        from_attributes=True,
    )
