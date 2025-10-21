from passlib.context import CryptContext
from models.ApplicationUser import ApplicationUser
from motor.motor_asyncio import AsyncIOMotorClient
from enums.ApplicationUserEnum import ApplicationUserEnum
from enums.DataBaseEnum import DataBaseEnum
from typing import Optional
from datetime import datetime, timedelta, timezone
from helpers.config import get_settings
from jose import jwt

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()

class ApplicationUserService:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.collection = db_client[DataBaseEnum.APPLICATION_USER_COLLECTION_NAME.value]

    async def init_indexes(self):
        """This method is to make sure that the username is unique by creating an index on it."""
        await self.collection.create_index("username", unique=True)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


    async def get_application_user_by_username(self, username: str) -> Optional[ApplicationUser]:
        application_user = await self.collection.find_one({"username": username})
        if application_user:
            return ApplicationUser(**application_user)
        return None

    async def create_application_user(self, username: str, password: str, role: str = ApplicationUserEnum.USER_ROLE) -> ApplicationUser:
        if await self.get_application_user_by_username(username):
            return None
        
        hashed_password = self.hash_password(password)
        role_value = role.value if isinstance(role, ApplicationUserEnum) else role # ensure role is string for mongoDB
        application_user = ApplicationUser(username=username, password_hash=hashed_password, role=role_value)
        result = await self.collection.insert_one(application_user.dict(exclude={"id"}))
        application_user.id = result.inserted_id
        return application_user
    
    async def authenticate_application_user(self, username: str, password: str) -> Optional[ApplicationUser]:
        application_user = await self.get_application_user_by_username(username)
        if application_user and self.verify_password(password, application_user.password_hash):
            return application_user
        return None

    def create_access_token(self, username: str, role: str, expires_delta: timedelta = None):
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {"sub": username, "role": role, "exp": datetime.now(timezone.utc) + expires_delta}
        encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encode_jwt
    
