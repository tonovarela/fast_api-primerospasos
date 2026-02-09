

from fastapi import APIRouter,File,UploadFile,HTTPException,status,shutil
import os
import uuid

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/bytes")
async def upload_bytes(file: bytes= File(...)):
    return {"filename": "archivo subido", "size": len(file)}

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    
    return {"filename": file.filename, "content_type": file.content_type}


@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    file_location = f"app/media/{file.filename}"
    
    
    if (file.content_type not in ["image/png","image/jpeg"]):
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imagen png o jpeg"
        )
    ext  = os.path.splitext(file.filename)[1]

    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join("app/media", filename)
        
    with open(file_path, "wb") as f:
         shutil.copyfileobj(file.file, f)
         
    return {"filename": filename, "content_type": file.content_type, "location": file_path}