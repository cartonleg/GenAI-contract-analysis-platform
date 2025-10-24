from motor.motor_asyncio import AsyncIOMotorClient
from enums.DataBaseEnum import DataBaseEnum
from models.Client import Client
from bson import ObjectId


class ClientService:
    def __init__(self, db_client: AsyncIOMotorClient): 
        self.collection = db_client[DataBaseEnum.CLIENT_COLLECTION_NAME.value]

    async def init_indexes(self):
        """This method is to make sure that the client name is unique by creating an index on it."""
        await self.collection.create_index("name", unique=True)

    async def get_client_by_name_and_application_user_id(self, name: str, application_user_id: str):

        client = await self.collection.find_one({"name": name, "application_user_id": ObjectId(application_user_id)})
        if client:
            return Client(**client)
        return None

    async def create_client_record(self, record_name: str, application_user_id: ObjectId):
        if await self.get_client_by_name_and_application_user_id(record_name, application_user_id):
            return None

        client = Client(name=record_name, application_user_id=application_user_id)
        result = await self.collection.insert_one(client.dict(exclude={"id"}))
        client.id = result.inserted_id
        return client
