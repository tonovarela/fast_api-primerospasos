
from fastapi import File,UploadFile,HTTPException,status
import os
import uuid
import shutil
MEDIA_DIR = "app/media" 
ALLOWED_CONTENT_TYPES = ["image/png","image/jpeg","application/pdf"]

MAX_MB  = int(os.getenv("MAX_MB","10")) 
CHUNKS  = 1024 * 1024 


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
    
    
    # class _ChunkCounter:
    #     def __init__(self, f):
    #         self._f = f
    #         self.calls = 0
    #         self.sizes = []
    #     def read(self, n=-1):
    #         data = self._f.read(n)
    #         if data:
    #             self.calls += 1
    #             self.sizes.append(len(data))
    #         return data
    #     def __getattr__(self, name):  # delega cualquier otro atributo
    #         return getattr(self._f, name)

    # reader = _ChunkCounter(file.file)
    
    
    
    with open(file_path, "wb") as buffer:
         shutil.copyfileobj(file.file, buffer,length=CHUNKS)
         
    size = os.path.getsize(file_path)
    if size > MAX_MB * CHUNKS:
         os.remove(file_path)
         raise HTTPException(
             status_code=status.HTTP_413_CONTENT_TOO_LARGE,
             detail=f"El archivo excede el tamaño máximo permitido de {MAX_MB} MB"
         )    
    
    
    return {"filename": filename,
            "content_type": file.content_type,
            "url": f"/media/{filename}",      
            "size": size            
            }
    
    
    

    