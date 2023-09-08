{#
The mongodb model definitions via Beanie. If a 'mongodb' option is selected and the `project_backend` is 'fastapi',
this will be moved to `src/models.py`.
#}
import os
from pydantic import EmailStr
from typing import List
from beanie import Document, Indexed, Link, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

class Destination(Document):
    name: Indexed(str, unique=True)
    subtitle: str
    description: str

    def __str__(self):
        return self.name

class Cruise(Document):
    name: Indexed(str, unique=True)
    subtitle: str
    description: str
    destinations: List[Link[Destination]]

    def __str__(self):
        return self.name


class InfoRequest(Document):
    name: str
    email: EmailStr
    notes: str
    cruise: Link[Cruise]


async def init_db():
    client = AsyncIOMotorClient(os.environ.get("DATABASE_URI"))
    await init_beanie(database=client.db_name, document_models=[Destination, Cruise, InfoRequest])