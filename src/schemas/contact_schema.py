from pydantic import BaseModel, ConfigDict


class ContactResoponse(BaseModel):
    name: str 
    phone: str

    model_config = ConfigDict(from_attributes=True)