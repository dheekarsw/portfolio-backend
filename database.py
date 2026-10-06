import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from beanie import init_beanie

from models import (
    Profile,
    Experience,
    Project
)


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

client = AsyncMongoClient(MONGO_URI)


async def init_database():

    database = client[MONGO_DATABASE]

    await init_beanie(
        database=database,
        document_models=[
            Profile,
            Experience,
            Project
        ]
    )