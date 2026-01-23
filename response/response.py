from pydantic import BaseModel

from dto.post_dto import PostBase
from typing import List,Literal,Optional


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


class PaginatedPost(BaseModel):    
    total:int
    page:int
    per_page:int
    total_pages:int
    has_prev:bool
    has_next:bool
    order_by:Literal["id","title"]
    direction:Literal["asc","desc"]
    search:Optional[str] =None    
    items:List[PostResponse]


