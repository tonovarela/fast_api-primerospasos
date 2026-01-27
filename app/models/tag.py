from __future__ import annotations
from sqlalchemy.orm import Mapped,mapped_column,relationship
from typing import  List, TYPE_CHECKING

from sqlalchemy import Integer,String
from app.core.db import Base

if TYPE_CHECKING:
    from .post import PostORM


class TagORM(Base):
    __tablename__ = "tags"
    id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str] = mapped_column(String(30), index=True, unique=True)        
    posts:Mapped[List["PostORM"]] = relationship(        
        secondary="posts_tags",
        back_populates="tags",
        lazy="selectin"    
        )  