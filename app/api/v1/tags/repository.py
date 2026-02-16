from typing import Optional

from fastapi import Query
from app.api.v1.tags.schemas import TagPublic
from app.models.tag import TagORM
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.services.pagination_service import paginate_query


class TagRepository:    
    def __init__(self,db:Session):
        self.db = db
    
    def list(self, search: Optional[str], order_by: str ="id", direction: str ="asc", page: int =1, per_page: int=10)-> tuple[int, list[TagORM]]:        
        query = select(TagORM)

        if search:
            query = query.where(func.lower(TagORM.name).like(f"%{search.lower()}%"))

        allowed_order ={
            "id": TagORM.id,
            "name": func.lower(TagORM.name),            
        }

        results =paginate_query(
            db=self.db,
            model=TagORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allow_order=allowed_order
        )        

        
        results["items"] = [TagPublic.model_validate(item) for item in results["items"]]
        return results["total"], results["items"]
        
    
    def create(self,name:str):
        normalized_name = name.strip().lower()
        if not normalized_name:
            return
        tag_obj = self.db.execute(            
                select(TagORM).where(func.lower(TagORM.name) == normalized_name.lower())
            ).scalar_one_or_none()
        

        if tag_obj:
            return tag_obj
                    
        tag_obj = TagORM(name=normalized_name)
        
        self.db.add(tag_obj)

        self.db.flush()
        self.db.commit()
        self.db.refresh(tag_obj)
         
        return tag_obj 
    
        
        
        
    