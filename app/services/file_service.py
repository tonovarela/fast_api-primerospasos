
from fastapi import File,UploadFile,HTTPException,status
import os
import uuid
import shutil
MEDIA_DIR = "app/media" 
ALLOWED_CONTENT_TYPES = ["image/png","image/jpeg","application/pdf"]


def ensure_media_dir()->None:
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)    
    

async def upload_bytes(file: bytes= File(...)):
    return {"filename": "archivo subido", "size": len(file)}


async def upload_file(file: UploadFile = File(...)):    
    return {"filename": file.filename, "content_type": file.content_type}



async def save_upload_file(file: UploadFile = File(...))->dict:                
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imagen png ,jpeg o pdf "
        )                
    ext  = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"    
    file_path = os.path.join(MEDIA_DIR, filename)    
    
    with open(file_path, "wb") as buffer:
         shutil.copyfileobj(file.file, buffer)

    return {"filename": filename,
            "content_type": file.content_type,
            "url": f"/media/{filename}"
            }
    
    
    

    