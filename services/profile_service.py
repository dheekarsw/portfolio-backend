from bson import ObjectId
from fastapi import HTTPException, UploadFile

from models import Profile

from cloudinary_service import (
    upload_image,
    delete_image,
    get_image_url
)

from image_service import compress_image


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


def validate_image_type(photo: UploadFile):
    if photo.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed"
        )


def validate_object_id(profile_id: str) -> ObjectId:
    try:
        return ObjectId(profile_id)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid profile ID"
        )


async def create_profile(
    name: str,
    description: str,
    email: str,
    photo: UploadFile
):
    # -----------------------------------------------------
    # Validate image
    # -----------------------------------------------------

    validate_image_type(photo)


    # -----------------------------------------------------
    # Read and compress image
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Create MongoDB ID
    # -----------------------------------------------------

    profile_id = ObjectId()


    # -----------------------------------------------------
    # Cloudinary public ID
    # -----------------------------------------------------

    public_id = f"profile_{profile_id}"


    # -----------------------------------------------------
    # Upload image
    # -----------------------------------------------------

    try:
        image = upload_image(
            file_content=file_content,
            public_id=public_id,
            folder="profiles"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


    # -----------------------------------------------------
    # Create MongoDB document
    # -----------------------------------------------------

    profile = Profile(
        id=profile_id,
        name=name,
        description=description,
        email=email,
        photo_public_id=image["public_id"]
    )


    # -----------------------------------------------------
    # Save MongoDB
    # -----------------------------------------------------

    try:
        await profile.insert()

    except Exception as e:

        # MongoDB failed.
        # Remove uploaded image from Cloudinary.

        try:
            delete_image(
                image["public_id"]
            )

        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save profile: {str(e)}"
        )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "message": "Profile created successfully",

        "data": {
            "id": str(profile.id),
            "name": profile.name,
            "description": profile.description,
            "email": profile.email,
            "photo_url": image["url"]
        }
    }


async def get_profiles():

    profiles = await Profile.find_all().to_list()

    result = []


    for profile in profiles:

        photo_url = None

        if profile.photo_public_id:
            photo_url = get_image_url(
                profile.photo_public_id
            )


        result.append({
            "id": str(profile.id),
            "name": profile.name,
            "description": profile.description,
            "email": profile.email,
            "photo_url": photo_url
        })


    return {
        "data": result
    }


async def get_profile(
    profile_id: str
):

    object_id = validate_object_id(
        profile_id
    )


    profile = await Profile.get(
        object_id
    )


    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )


    photo_url = None

    if profile.photo_public_id:
        photo_url = get_image_url(
            profile.photo_public_id
        )


    return {
        "data": {
            "id": str(profile.id),
            "name": profile.name,
            "description": profile.description,
            "email": profile.email,
            "photo_url": photo_url
        }
    }


async def update_profile(
    profile_id: str,
    name: str,
    description: str,
    email: str,
    photo: UploadFile | None = None
):

    object_id = validate_object_id(
        profile_id
    )


    profile = await Profile.get(
        object_id
    )


    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )


    # -----------------------------------------------------
    # Update text fields
    # -----------------------------------------------------

    profile.name = name
    profile.description = description
    profile.email = email


    # -----------------------------------------------------
    # Update photo
    # -----------------------------------------------------

    if photo is not None:

        validate_image_type(photo)

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


        old_public_id = profile.photo_public_id


        # Use a new public ID for the replacement image.
        new_public_id = (
            f"profile_{profile_id}_new"
        )


        # -------------------------------------------------
        # Upload new image
        # -------------------------------------------------

        try:

            image = upload_image(
                file_content=file_content,
                public_id=new_public_id,
                folder="profiles"
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload new image: {str(e)}"
            )


        # -------------------------------------------------
        # Update MongoDB
        # -------------------------------------------------

        profile.photo_public_id = image["public_id"]


        try:

            await profile.save()

        except Exception as e:

            # Database update failed.
            # Remove the new image.

            try:
                delete_image(
                    image["public_id"]
                )

            except Exception:
                pass

            raise HTTPException(
                status_code=500,
                detail=f"Failed to update profile: {str(e)}"
            )


        # -------------------------------------------------
        # Delete old image
        # -------------------------------------------------

        if old_public_id:

            try:
                delete_image(
                    old_public_id
                )

            except Exception:
                pass


    else:

        # -------------------------------------------------
        # Save text changes only
        # -------------------------------------------------

        try:

            await profile.save()

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Failed to update profile: {str(e)}"
            )


    # -----------------------------------------------------
    # Generate current photo URL
    # -----------------------------------------------------

    photo_url = None

    if profile.photo_public_id:

        photo_url = get_image_url(
            profile.photo_public_id
        )


    return {
        "message": "Profile updated successfully",

        "data": {
            "id": str(profile.id),
            "name": profile.name,
            "description": profile.description,
            "email": profile.email,
            "photo_url": photo_url
        }
    }


async def delete_profile(
    profile_id: str
):

    object_id = validate_object_id(
        profile_id
    )


    profile = await Profile.get(
        object_id
    )


    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )


    # -----------------------------------------------------
    # Delete Cloudinary image
    # -----------------------------------------------------

    if profile.photo_public_id:

        try:

            delete_image(
                profile.photo_public_id
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image: {str(e)}"
            )


    # -----------------------------------------------------
    # Delete MongoDB document
    # -----------------------------------------------------

    await profile.delete()


    return {
        "message": "Profile deleted successfully"
    }