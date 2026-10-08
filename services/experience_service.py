from datetime import date

from bson import ObjectId
from fastapi import HTTPException, UploadFile

from models import Experience

from cloudinary_service import (
    upload_image,
    upload_file,
    delete_file,
    get_image_url,
    get_file_url
)

from image_service import compress_image


IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

CERTIFICATE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp"
}


def validate_object_id(
    experience_id: str
) -> ObjectId:

    try:
        return ObjectId(experience_id)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid experience ID"
        )


def validate_photo(
    photo: UploadFile
):

    if photo.content_type not in IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Photo must be JPG, PNG, or WEBP"
        )


def validate_certificate(
    certificate: UploadFile
):

    if certificate.content_type not in CERTIFICATE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Certificate must be PDF, JPG, PNG, or WEBP"
        )


async def upload_photo(
    photo: UploadFile,
    public_id: str
):

    validate_photo(photo)

    original_file = await photo.read()

    try:
        file_content, content_type = compress_image(
            original_file
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image: {str(e)}"
        )

    return upload_image(
        file_content=file_content,
        public_id=public_id,
        folder="experiences"
    )


async def upload_certificate(
    certificate: UploadFile,
    public_id: str
):

    validate_certificate(certificate)

    file_content = await certificate.read()

    # filename untuk memberikan .pdf agar di cloudinary ada format pdf nya, cek settingan di history chat "Upload PDF Cloudinary FastAPI"
    # filename = certificate.filename or "certificate"

    return upload_file(
        file_content=file_content,
        public_id=public_id,
        folder="certificate"
    )


async def create_experience(
    name: str,
    description: str,
    start_date: date,
    end_date: date | None,
    location: str,
    photo: UploadFile | None,
    certificate: UploadFile | None
):

    if end_date and end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date"
        )


    experience_id = ObjectId()

    photo_public_id = None
    certificate_public_id = None


    try:

        # -------------------------
        # Upload photo
        # -------------------------

        if photo:

            image = await upload_photo(
                photo,
                f"experience_{experience_id}_photo"
            )

            photo_public_id = image["public_id"]


        # -------------------------
        # Upload certificate
        # -------------------------

        if certificate:

            file = await upload_certificate(
                certificate,
                f"experience_{experience_id}_certificate"
            )

            certificate_public_id = file["public_id"]


        # -------------------------
        # Save MongoDB
        # -------------------------

        experience = Experience(
            id=experience_id,

            name=name,
            description=description,

            start_date=start_date,
            end_date=end_date,

            location=location,

            photo_public_id=photo_public_id,
            certificate_public_id=certificate_public_id
        )

        await experience.insert()


    except Exception as e:

        # Cleanup Cloudinary
        if photo_public_id:
            try:
                delete_file(
                    photo_public_id,
                    resource_type="image"
                )
            except Exception:
                pass

        if certificate_public_id:
            try:
                delete_file(
                    certificate_public_id,
                    resource_type="raw"
                )
            except Exception:
                pass

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create experience: {str(e)}"
        )


    return {
        "message": "Experience created successfully",
        "data": serialize_experience(
            experience
        )
    }


async def get_experiences():

    experiences = await Experience.find_all().to_list()

    return {
        "data": [
            serialize_experience(
                experience
            )
            for experience in experiences
        ]
    }


async def get_experience(
    experience_id: str
):

    object_id = validate_object_id(
        experience_id
    )

    experience = await Experience.get(
        object_id
    )

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Experience not found"
        )

    return {
        "data": serialize_experience(
            experience
        )
    }

async def update_experience(
    experience_id: str,

    name: str,
    description: str,

    start_date: date,
    end_date: date | None,

    location: str,

    photo: UploadFile | None,
    certificate: UploadFile | None
):

    object_id = validate_object_id(
        experience_id
    )

    experience = await Experience.get(
        object_id
    )

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Experience not found"
        )


    if end_date and end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date"
        )


    experience.name = name
    experience.description = description
    experience.start_date = start_date
    experience.end_date = end_date
    experience.location = location


    # ---------------------------------
    # Replace photo
    # ---------------------------------

    if photo:

        old_photo = experience.photo_public_id

        new_photo = await upload_photo(
            photo,
            f"experience_{experience_id}_photo_new"
        )

        experience.photo_public_id = new_photo[
            "public_id"
        ]

        if old_photo:

            try:
                delete_file(
                    old_photo
                )
            except Exception:
                pass


    # ---------------------------------
    # Replace certificate
    # ---------------------------------

    if certificate:

        old_certificate = (
            experience.certificate_public_id
        )

        new_certificate = await upload_certificate(
            certificate,
            f"experience_{experience_id}_certificate_new"
        )

        experience.certificate_public_id = (
            new_certificate["public_id"]
        )


        if old_certificate:

            try:
                delete_file(
                    old_certificate
                )
            except Exception:
                pass


    # ---------------------------------
    # Save changes
    # ---------------------------------

    try:

        await experience.save()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update experience: {str(e)}"
        )


    return {
        "message": "Experience updated successfully",
        "data": serialize_experience(
            experience
        )
    }



async def delete_experience(
    experience_id: str
):

    object_id = validate_object_id(
        experience_id
    )

    experience = await Experience.get(
        object_id
    )

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Experience not found"
        )


    if experience.photo_public_id:

        try:
            delete_file(
                experience.photo_public_id,
                resource_type="image"
            )
        except Exception:
            pass


    if experience.certificate_public_id:

        try:
            delete_file(
                experience.certificate_public_id,
                resource_type="raw"
            )
        except Exception:
            pass


    await experience.delete()


    return {
        "message": "Experience deleted successfully"
    }


def serialize_experience(
    experience: Experience
):

    photo_url = None
    certificate_url = None


    if experience.photo_public_id:
        photo_url = get_image_url(
            experience.photo_public_id
        )


    if experience.certificate_public_id:
        certificate_url = get_file_url(
            experience.certificate_public_id
        )


    return {
        "id": str(experience.id),

        "name": experience.name,

        "description": experience.description,

        "start_date": experience.start_date,

        "end_date": experience.end_date,

        "location": experience.location,

        "photo_url": photo_url,

        "certificate_url": certificate_url
    }