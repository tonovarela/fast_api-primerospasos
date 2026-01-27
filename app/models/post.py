
from datetime import datetime
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Integer,String, Table,Text,DateTime,UniqueConstraint,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.core.db import Base

if TYPE_CHECKING:
    from .author import AuthorORM
    from .tag import TagORM

posts_tags = Table(
    'posts_tags',
    Base.metadata,
    Column('post_id', ForeignKey('posts.id',ondelete="CASCADE") ,primary_key=True),
    Column('tag_id', ForeignKey('tags.id',ondelete="CASCADE"), primary_key=True)
)

class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ =(UniqueConstraint('title', name='uq_post_title'),)
    # Definición de columnas aquí
    id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    title:Mapped[str] = mapped_column(String(100), nullable=False,index=True)    
    content:Mapped[str] = mapped_column(Text, nullable=False)    
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)    
    updated_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)    
    author_id:Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))    
    author:Mapped[Optional["AuthorORM"]] = relationship( back_populates="posts")    
    tags:Mapped[List["TagORM"]] = relationship(        
        secondary=posts_tags,
        back_populates="posts",
        lazy="selectin",
        passive_deletes=True
        )