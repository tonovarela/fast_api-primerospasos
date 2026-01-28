from math import ceil
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import List, Tuple

from app.models import PostORM, AuthorORM, TagORM


class PostRespository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        stmt = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def search(self, query: Optional[str], order_by: str, direction: str, page: int, per_page: int) -> Tuple[int, List[PostORM]]:
        results = select(PostORM).options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author)
        )

        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))
        total = self.db.scalar(
            select(func.count()).select_from(results.subquery())) or 0

        if total == 0:
            return 0, []

        total_pages = ceil(total/per_page)
        current_page = min(page, max(1, total_pages))

        if order_by == "id":
            order_col = PostORM.id
        else:
            order_col = func.lower(PostORM.title)

        results = results.order_by(
            order_col.desc() if direction == "desc" else order_col.asc())

        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(
            per_page).offset(start)).scalars().all()

        return total, items

    def by_tags(self, tags: List[str]) -> List[PostORM]:
        tags_lower = [tag.strip().lower() for tag in tags if tag.strip()]

        if not tags_lower:
            return []

        post_list = select(PostORM).options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author)

        ).where(PostORM.tags.any(func.lower(TagORM.name).in_(tags_lower))).order_by(PostORM.id.asc())

        posts = self.db.execute(post_list).scalars().all()

        return posts

    def ensure_author(self,name:str,email:str)->AuthorORM:
        author_obj = self.db.execute(select(AuthorORM).where(AuthorORM.email == email)).scalar_one_or_none()    
        if author_obj:
            return author_obj
        
        author_obj = AuthorORM(name=name, email=email)
        self.db.add(author_obj)
        self.db.flush()  
        return author_obj
    
    def ensure_tags(self,name:str)->TagORM:
        tag_obj = self.db.execute(
                select(TagORM).where(func.lower(TagORM.name) == name.lower())
            ).scalar_one_or_none()
        if tag_obj:
            return tag_obj
                    
        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()  
        return tag_obj # Asegura que tag_obj tenga un ID asignado
     
    
    def create(self,title:str,content:str,author:Optional[dict],tags:List[dict])->PostORM:
        author_ob= None
        if author:
            author_ob = self.ensure_author(author["name"],author["email"])
        post = PostORM(title=title,content=content,author=author_ob)
        for tag in tags:
            tab_obj= self.ensure_tags(tag["name"])
            post.tags.append(tab_obj)
            
        self.db.add(post)  
        self.db.flush()
        self.db.refresh(post)        
        return post    
    
    def delete(self,post:PostORM)->None:                
        self.db.delete(post)            
           
    def update(self, post:PostORM,updates)->PostORM:        
        for key, value in updates.items():
            setattr(post, key, value)                
        return post
                          
        
        
        