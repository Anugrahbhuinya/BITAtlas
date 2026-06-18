from motor.motor_asyncio import AsyncIOMotorClient
from app.core import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client[config.MONGO_DB]

def get_database():
    return db
