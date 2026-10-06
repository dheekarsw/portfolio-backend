from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from datetime import date

from services.project_service import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("")
async def create_project_endpoint(
    name: str = Form(...),
    description: str = Form(...),

    date: date = Form(...),

    location: str = Form(...),

    project_url: str | None = Form(None),

    photo: UploadFile | None = File(None),
    certificate: UploadFile | None = File(None)
):
    return await create_project(
        name=name,
        description=description,
        date=date,
        location=location,
        project_url=project_url,
        photo=photo,
        certificate=certificate
    )


@router.get("")
async def get_projects_endpoint():
    return await get_projects()


@router.get("/{project_id}")
async def get_project_endpoint(
    project_id: str
):
    return await get_project(
        project_id
    )


@router.put("/{project_id}")
async def update_project_endpoint(
    project_id: str,

    name: str = Form(...),
    description: str = Form(...),

    date: date = Form(...),

    location: str = Form(...),

    project_url: str | None = Form(None),

    photo: UploadFile | None = File(None),
    certificate: UploadFile | None = File(None)
):
    return await update_project(
        project_id=project_id,
        name=name,
        description=description,
        date=date,
        location=location,
        project_url=project_url,
        photo=photo,
        certificate=certificate
    )


@router.delete("/{project_id}")
async def delete_project_endpoint(
    project_id: str
):
    return await delete_project(
        project_id
    )