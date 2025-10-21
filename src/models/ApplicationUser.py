from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from enums.ApplicationUserEnum import ApplicationUserEnum

class ApplicationUser(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    username: str
    password_hash: str
    role: str

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoder = {ObjectId: str}

    def dict(self, **kwargs):
        """this method is to override dict to handle ObjectId serialization"""
        d = super().model_dump(**kwargs)
        if d.get("_id"):
            d["_id"] = str(d["_id"])
        return d