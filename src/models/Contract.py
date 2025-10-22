from pydantic import BaseModel, Field
from bson import ObjectId, Binary
from typing import Optional
from fastapi import UploadFile

class Contract(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    title: str
    client_id: ObjectId
    application_user_id: ObjectId
    content: Binary

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