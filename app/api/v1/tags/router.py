
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm  import Session
from sqlalchemy.exc import  SQLAlchemyError

from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic
from app.core.db import get_db
from app.core.security import get_currrent_user


router = APIRouter(prefix="/tags",tags=["tags"])


@router.get("",response_model=list[TagPublic],response_description="List of tags")
def list_tags(search: Optional[str] = None, 
              order_by: str = "id", 
              direction: str = "asc",
              page: int = 1, 
              per_page: int = 10,
              db: Session = Depends(get_db)):
    repository = TagRepository(db)
    tags = []
    try:
        total, tags = repository.list(search=search, order_by=order_by, direction=direction, page=page, per_page=per_page)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))    
    return tags 


@router.post("",response_model=TagPublic,response_description="Tag created successfully", status_code=status.HTTP_201_CREATED)
def create_tag(tag:TagCreate, db:Session = Depends(get_db)):
    respository = TagRepository(db)
    try:
        tag_obj = respository.create(name=tag.name)
        
            
        print(f"Tag created with ID: {tag_obj.id}")     
    except SQLAlchemyError as e:    
        db.rollback()
        print(f"Error creating tag: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return tag_obj
             
        
    


