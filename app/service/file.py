from xmlrpc.client import boolean
import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends,Response, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session


from model.user import User
# from utils.check_role import chek_permission
from utils.db import SessionLocal
from utils.image_tools import write_image,open_image
from utils.file.file import upload_file
from schema.file import uploadFile

files_routes = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@files_routes.post("/staff/upload_cv", tags=["Staff"])
async def upload_cv_staff(
    file: UploadFile,
    response: Response, 
    db: Session = Depends(get_db)
):
    try:
        destination = Path(f"media/cv/{uuid.uuid4()}-{file.filename}")
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            path = Path(buffer.name)
    finally:
        file.file.close()
    return path


@files_routes.post("/upload_file", tags=["Files"])
def upload_single_file(
    file: UploadFile,
    path: str,
    db: Session = Depends(get_db)
):
    image_route = upload_file(file, path)
    return {"path": image_route}