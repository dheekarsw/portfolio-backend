from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from services.profile_service import (
    create_profile,
    get_profiles,
    get_profile,
    update_profile,
    delete_profile
)


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"]
)


@router.post("")
async def create_profile_endpoint(
    name: str = Form(...),
    description: str = Form(...),
    email: str = Form(...),
    photo: UploadFile = File(...)
):
    return await create_profile(
        name=name,
        description=description,
        email=email,
        photo=photo
    )


@router.get("")
async def get_profiles_endpoint():
    return await get_profiles()


@router.get("/{profile_id}")
async def get_profile_endpoint(
    profile_id: str
):
    return await get_profile(
        profile_id
    )


@router.put("/{profile_id}")
async def update_profile_endpoint(
    profile_id: str,
    name: str = Form(...),
    description: str = Form(...),
    email: str = Form(...),
    photo: UploadFile | None = File(None)
):
    return await update_profile(
        profile_id=profile_id,
        name=name,
        description=description,
        email=email,
        photo=photo
    )


@router.delete("/{profile_id}")
async def delete_profile_endpoint(
    profile_id: str
):
    return await delete_profile(
        profile_id
    )