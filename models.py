from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import date


class Profile(Document):
    name: str = Field(min_length=1)
    description: str
    email: EmailStr

    # ID gambar di Cloudinary
    photo_public_id: Optional[str] = None

    class Settings:
        name = "profiles"


class Experience(Document):
    name: str = Field(min_length=1)
    description: str

    start_date: date
    end_date: Optional[date] = None

    location: str

    # ID file di Cloudinary
    photo_public_id: Optional[str] = None
    certificate_public_id: Optional[str] = None

    class Settings:
        name = "experiences"


class Project(Document):
    name: str = Field(min_length=1)
    description: str

    date: date
    location: str

    project_url: Optional[str] = None

    # ID file di Cloudinary
    photo_public_id: Optional[str] = None
    certificate_public_id: Optional[str] = None

    class Settings:
        name = "projects"