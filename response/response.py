from pydantic import BaseModel
from dto.post_dto import PostBase


class PostResponse(PostBase):
    id:int    
    content:str
    
class PostSummaryResponse(BaseModel):
    id:int    
    title:str
        
class PostCreateResponse(BaseModel):
    message:str
    data:PostBase    

class PostUpdateResponse(PostCreateResponse):
    pass


