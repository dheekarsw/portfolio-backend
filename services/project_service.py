from datetime import date

from bson import ObjectId
from fastapi import HTTPException, UploadFile

from models import Project

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
    project_id: str
) -> ObjectId:

    try:
        return ObjectId(project_id)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID"
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
        folder="projects"
    )


async def upload_certificate(
    certificate: UploadFile,
    public_id: str
):

    validate_certificate(certificate)

    file_content = await certificate.read()

    return upload_file(
        file_content=file_content,
        public_id=public_id,
        folder="certificate"
    )


async def create_project(
    name: str,
    description: str,
    date: date,
    location: str,
    project_url: str | None,
    photo: UploadFile | None,
    certificate: UploadFile | None
):

    project_id = ObjectId()

    photo_public_id = None
    certificate_public_id = None


    try:

        if photo:

            image = await upload_photo(
                photo,
                f"project_{project_id}_photo"
            )

            photo_public_id = image["public_id"]


        if certificate:

            file = await upload_certificate(
                certificate,
                f"project_{project_id}_certificate"
            )

            certificate_public_id = file["public_id"]


        project = Project(
            id=project_id,

            name=name,
            description=description,

            date=date,
            location=location,

            project_url=project_url,

            photo_public_id=photo_public_id,
            certificate_public_id=certificate_public_id
        )

        await project.insert()


    except Exception as e:

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
            detail=f"Failed to create project: {str(e)}"
        )


    return {
        "message": "Project created successfully",
        "data": serialize_project(
            project
        )
    }


async def get_projects():

    projects = await Project.find_all().to_list()

    return {
        "data": [
            serialize_project(project)
            for project in projects
        ]
    }


async def get_project(
    project_id: str
):

    object_id = validate_object_id(
        project_id
    )

    project = await Project.get(
        object_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    return {
        "data": serialize_project(
            project
        )
    }


async def update_project(
    project_id: str,

    name: str,
    description: str,

    date: date,
    location: str,

    project_url: str | None,

    photo: UploadFile | None,
    certificate: UploadFile | None
):

    object_id = validate_object_id(
        project_id
    )

    project = await Project.get(
        object_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    project.name = name
    project.description = description
    project.date = date
    project.location = location
    project.project_url = project_url


    if photo:

        old_photo = project.photo_public_id

        image = await upload_photo(
            photo,
            f"project_{project_id}_photo_new"
        )

        project.photo_public_id = image[
            "public_id"
        ]


        if old_photo:

            try:
                delete_file(
                    old_photo
                )
            except Exception:
                pass


    if certificate:

        old_certificate = (
            project.certificate_public_id
        )

        certificate_file = await upload_certificate(
            certificate,
            f"project_{project_id}_certificate_new"
        )

        project.certificate_public_id = (
            certificate_file["public_id"]
        )


        if old_certificate:

            try:
                delete_file(
                    old_certificate
                )
            except Exception:
                pass


    try:

        await project.save()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update project: {str(e)}"
        )


    return {
        "message": "Project updated successfully",
        "data": serialize_project(
            project
        )
    }



async def delete_project(
    project_id: str
):

    object_id = validate_object_id(
        project_id
    )

    project = await Project.get(
        object_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


    if project.photo_public_id:

        try:
            delete_file(
                project.photo_public_id,
                resource_type="image"
            )
        except Exception:
            pass


    if project.certificate_public_id:

        try:
            delete_file(
                project.certificate_public_id,
                resource_type="raw"
            )
        except Exception:
            pass


    await project.delete()


    return {
        "message": "Project deleted successfully"
    }


def serialize_project(
    project: Project
):

    photo_url = None
    certificate_url = None


    if project.photo_public_id:

        photo_url = get_image_url(
            project.photo_public_id
        )


    if project.certificate_public_id:

        certificate_url = get_file_url(
            project.certificate_public_id
        )


    return {
        "id": str(project.id),

        "name": project.name,

        "description": project.description,

        "date": project.date,

        "location": project.location,

        "project_url": project.project_url,

        "photo_url": photo_url,

        "certificate_url": certificate_url
    }