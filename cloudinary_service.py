import os

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from dotenv import load_dotenv

load_dotenv()


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def upload_image(
    file_content: bytes,
    public_id: str,
    folder: str
):
    result = cloudinary.uploader.upload(
        file_content,
        public_id=public_id,
        folder=folder,
        resource_type="image"
    )

    return {
        "public_id": result["public_id"],
        "url": result["secure_url"]
    }


def upload_file(
    file_content: bytes,
    public_id: str,
    folder: str
):
    result = cloudinary.uploader.upload(
        file_content,
        public_id=public_id,
        folder=folder,
        resource_type="raw"
    )

    return {
        "public_id": result["public_id"],
        "url": result["secure_url"]
    }


def delete_image(
    public_id: str
):
    cloudinary.uploader.destroy(
        public_id,
        resource_type="image"
    )


def delete_file(
    public_id: str
):
    cloudinary.uploader.destroy(
        public_id,
        resource_type="raw"
    )


def get_image_url(
    public_id: str
):
    return cloudinary.CloudinaryImage(
        public_id
    ).build_url(
        secure=True
    )


def get_file_url(
    public_id: str
):
    url, options = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="raw",
        secure=True
    )

    return url