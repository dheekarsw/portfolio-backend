from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from datetime import date

from services.experience_service import (
    create_experience,
    get_experiences,
    get_experience,
    update_experience,
    delete_experience
)


router = APIRouter(
    prefix="/experiences",
    tags=["Experiences"]
)


@router.post("")
async def create_experience_endpoint(
    name: str = Form(...),
    description: str = Form(...),

    start_date: date = Form(...),
    end_date: date | None = Form(None),

    location: str = Form(...),

    photo: UploadFile | None = File(None),
    certificate: UploadFile | None = File(None)
):
    return await create_experience(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        location=location,
        photo=photo,
        certificate=certificate
    )


@router.get("")
async def get_experiences_endpoint():
    return await get_experiences()


@router.get("/{experience_id}")
async def get_experience_endpoint(
    experience_id: str
):
    return await get_experience(
        experience_id
    )


@router.put("/{experience_id}")
async def update_experience_endpoint(
    experience_id: str,

    name: str = Form(...),
    description: str = Form(...),

    start_date: date = Form(...),
    end_date: date | None = Form(None),

    location: str = Form(...),

    photo: UploadFile | None = File(None),
    certificate: UploadFile | None = File(None)
):
    return await update_experience(
        experience_id=experience_id,
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        location=location,
        photo=photo,
        certificate=certificate
    )


@router.delete("/{experience_id}")
async def delete_experience_endpoint(
    experience_id: str
):
    return await delete_experience(
        experience_id
    )