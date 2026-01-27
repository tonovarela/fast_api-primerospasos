from math import ceil
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session,selectinload,joinedload
from typing import List,Tuple

from app.models import PostORM,AuthorORM,TagORM


class PostRespository:
    def __init__(self,db:Session):
        self.db = db
        
    
    def get(self,post_id:int)->Optional[PostORM]:    
         stmt = select(PostORM).where(PostORM.id == post_id)
         return self.db.execute(stmt).scalar_one_or_none()         
     
    def search(self,query:Optional[str],order_by:str,direction:str,page:int,per_page:int)->Tuple[int,List[PostORM]]:
        results = select(PostORM).options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author)
        )
                
        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))        
        total = self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        
        if total==0:
            return 0,[]
                
        total_pages = ceil(total/per_page)
        current_page = min(page, max(1, total_pages))
        
        if order_by == "id":
            order_col = PostORM.id
        else:
            order_col = func.lower(PostORM.title)
        
        results = results.order_by(order_col.desc() if direction == "desc" else order_col.asc())
                               
        
        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(per_page).offset(start)).scalars().all()
                
        return total, items
        
         
        
    