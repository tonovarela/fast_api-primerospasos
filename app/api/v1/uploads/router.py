from fastapi import APIRouter,File,UploadFile
from app.services.file_service import upload_bytes,upload_file,save_upload_file,ensure_media_dir

router = APIRouter(prefix="/uploads", tags=["uploads"])




@router.post("/bytes")
async def upload_bytes(file: bytes= File(...)):
    return await upload_bytes(file)

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):    
    return await upload_file(file)


@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    return await save_upload_file(file)
    
    
    
    