
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm  import Session
from sqlalchemy.exc import  SQLAlchemyError

from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic
from app.core.db import get_db
from app.core.security import get_currrent_user


router = APIRouter(prefix="/tags",tags=["tags"])






@router.get("",response_description="List of tags")
def list_tags(page: int = Query(1, ge=1), 
              per_page:int =Query(10, ge=1, le=100),
              order_by: str = Query("id", pattern="^(id|name)$"), 
              direction: str = Query("asc", pattern="^(asc|desc)$"),
              search: Optional[str] = Query(None, max_length=50),
              db: Session = Depends(get_db)):
    repository = TagRepository(db)
    tags = []
    try:
         tags = repository.list(search=search, order_by=order_by, direction=direction, page=page, per_page=per_page)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))   
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
        
         
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
             
        
    
@router.delete("/{tag_id}",response_model=TagPublic,response_description="Tag deleted successfully")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    repository = TagRepository(db)
    try:
        tag_obj = repository.delete(tag_id=tag_id)
        if not tag_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return tag_obj

@router.put("/{tag_id}",response_model=TagPublic,response_description="Tag updated successfully")
def update_tag(tag_id: int, tag: TagCreate, db: Session = Depends(get_db)):
    repository = TagRepository(db)
    try:
        tag_obj = repository.update(tag_id=tag_id, name=tag.name)
        if not tag_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return tag_obj