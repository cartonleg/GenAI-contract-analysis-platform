from pydantic import BaseModel
from enums.ApplicationUserEnum import ApplicationUserEnum

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: ApplicationUserEnum
