from pydantic import BaseModel, ConfigDict


class AbstractModel(BaseModel):
    """Abstract pydantic model for general configuration.

    This model is used to set general configuration for
    pydantic models. In pydantic, the model_config is inherited from the parent class
    and only the parameter explicitly set in the ConfigDict are overriden. Therefore, all models in the application
    have to extend this instead of BaseModel.
    """
    model_config = ConfigDict(
        # remove whitespaces in the beggining / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instanciate model from attribute of another class
        from_attributes=True,
    )