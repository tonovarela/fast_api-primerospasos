from typing import Optional

from fastapi import Query
from app.models.tag import TagORM
from sqlalchemy.orm import Session
from sqlalchemy import func, select


class TagRepository:    
    def __init__(self,db:Session):
        self.db = db
    
    def list(self, search: Optional[str], order_by: str ="id", direction: str ="asc", page: int =1, per_page: int=10)-> tuple[int, list[TagORM]]:
        query = select(TagORM)
        
        if search:
            query = query.where(func.lower(TagORM.name).like(f"%{search.strip().lower()}%"))
        
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        if total == 0:
            return 0, []
        
        total_pages = (total + per_page -1) // per_page
        current_page = min(page, max(1, total_pages))
        
        order_col = TagORM.id if order_by == "id" else func.lower(TagORM.name)
        query = query.order_by(order_col.desc() if direction == "desc" else order_col.asc())
        
        start = (current_page -1) * per_page
        items = self.db.execute(query.limit(per_page).offset(start)).scalars().all()
        
        return total, items
        
    
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
        return tag_obj 
    
        
        
        
    