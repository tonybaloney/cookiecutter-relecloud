{#
The mongodb model definitions via Beanie. If a 'mongodb' option is selected and the `project_backend` is 'fastapi',
this will be moved to `src/models.py`.
#}
from pydantic import EmailStr
from typing import List
from beanie import Document, Indexed, Link

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
