from typing import Optional

from fastapi import Query
from app.api.v1.tags.schemas import TagPublic
from app.models.post import PostORM,posts_tags
from app.models.tag import TagORM
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.services.pagination_service import paginate_query


class TagRepository:    
    def __init__(self,db:Session):
        self.db = db
    
    def list(self, search: Optional[str], order_by: str ="id", direction: str ="asc", page: int =1, per_page: int=10):        
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
        print(results)
        return results

        
    
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
    


    def delete(self,tag_id: int):
        tag_obj = self.get(tag_id)
        if not tag_obj:
            return None
        self.db.delete(tag_obj)
        self.db.flush()
        self.db.commit()
    
        return tag_obj
    
    def update(self, tag_id: int, name: str):
        tag_obj = self.get(tag_id)

        if not tag_obj:
            return None
        if name is not None:
            tag_obj.name = name.strip().lower()
        self.db.add(tag_obj)
        self.db.flush()
        self.db.refresh(tag_obj)
        self.db.commit()
        return tag_obj
    
    def get(self,tag_id:int)->Optional[TagORM]:
        tag_find =select(TagORM).where(TagORM.id == tag_id)
        return self.db.execute(tag_find).scalar_one_or_none() 
    
    def most_popular(self)->Optional[dict]:
        row =(
            self.db.execute(
                select(
                    TagORM.id.label("id"),
                    TagORM.name.label("name"),
                    func.count(PostORM.id).label("uses")
                )
                .join(posts_tags,posts_tags.c.tag_id == TagORM.id)
                .join(PostORM,   PostORM.id == posts_tags.c.post_id)
                .group_by(TagORM.id,TagORM.name)
                .order_by(func.count(PostORM.id).desc(),func.lower(TagORM.name).asc())
                .limit(1)
            )
            .mappings()
            .first()
        )
        
        return  dict(row) if row else None