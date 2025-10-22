from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class Client(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    application_user_id: ObjectId
    name: str
    
    class Config:
        arbitrary_types_allowed = True
        populated_by_name = True
        json_encoders = {ObjectId: str}

    def dict(self, **kwargs):
        """this method is to override dict to handle ObjectId serialization"""
        d = super().model_dump(**kwargs)
        if d.get("_id"):
            d["_id"] = str(d["_id"])
        return d