
import os
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException, Path, status,Depends
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict

from typing import Optional, List, Union, Literal
from math import ceil

from sqlalchemy import create_engine,Integer,String,Text,DateTime,select,func,UniqueConstraint,ForeignKey,Table,Column
from sqlalchemy.orm import sessionmaker,Session,DeclarativeBase,Mapped,mapped_column,relationship,selectinload,joinedload
from sqlalchemy.exc import SQLAlchemyError,IntegrityError

from dotenv import load_dotenv
load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

# print(f"Conectando a la base de datos en: {DATABASE_URL}")

# engine_kwargs = {}
# if DATABASE_URL.startswith("sqlite"):
#     engine_kwargs["connect_args"] = {"check_same_thread": False}
    
    
    
# engine = create_engine(DATABASE_URL, echo=True,future=True, **engine_kwargs) 
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


# class Base(DeclarativeBase):
#     pass

# posts_tags = Table(
#     'posts_tags',
#     Base.metadata,
#     Column('post_id', ForeignKey('posts.id',ondelete="CASCADE") ,primary_key=True),
#     Column('tag_id', ForeignKey('tags.id',ondelete="CASCADE"), primary_key=True)
# )

# class AuthorORM(Base):
#     __tablename__ = "authors"
#     id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
#     name:Mapped[str] = mapped_column(String(100), nullable=False)
#     email:Mapped[str] = mapped_column(String(100), index=True, unique=True)    
#     posts:Mapped[List["PostORM"]] = relationship( back_populates="author")
        
# class TagORM(Base):
#     __tablename__ = "tags"
#     id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
#     name:Mapped[str] = mapped_column(String(30), index=True, unique=True)        
#     posts:Mapped[List["PostORM"]] = relationship(        
#         secondary=posts_tags,
#         back_populates="tags",
#         lazy="selectin"    
#         )    

# class PostORM(Base):
#     __tablename__ = "posts"
#     __table_args__ =(UniqueConstraint('title', name='uq_post_title'),)
#     # Definición de columnas aquí
#     id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
#     title:Mapped[str] = mapped_column(String(100), nullable=False,index=True)    
#     content:Mapped[str] = mapped_column(Text, nullable=False)    
#     created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)    
#     updated_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)    
#     author_id:Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))    
#     author:Mapped[Optional["AuthorORM"]] = relationship( back_populates="posts")    
#     tags:Mapped[List["TagORM"]] = relationship(        
#         secondary=posts_tags,
#         back_populates="posts",
#         lazy="selectin",
#         passive_deletes=True
#         )
        
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
   
app = FastAPI(title="Mini Blog")                                 

@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get("/posts", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parámetro obsoleto, usa 'query o search' en su lugar."
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar por título",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"
    ),
    per_page: int = Query(
        10, ge=1, le=50,
        description="Número de resultados (1-50)"
    ),
    page: int = Query(
        1, ge=1,
        description="Número de página (>=1)"
    ),
    order_by: Literal["id", "title"] = Query(
        "id", description="Campo de orden"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden"
    ),
    db: Session = Depends(get_db)
):
    results = select(PostORM)
    
    query = query or text
    
    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))

    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0

    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    
    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)
    
    results = results.order_by(order_col.desc() if direction == "desc" else order_col.asc())
                   
    if total_pages == 0:
        items :List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(per_page).offset(start)).scalars().all()

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )


@app.get("/posts/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=2,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=fastapi",
        
    ),
    db: Session = Depends(get_db)
):
    tags_lower = [tag.strip().lower() for tag in tags if tag.strip()]
    
    if not tags_lower:
        return []
    
    post_list = select(PostORM).options(
        selectinload(PostORM.tags),
        joinedload(PostORM.author)
        
    ).where(PostORM.tags.any(func.lower(TagORM.name).in_(tags_lower))).order_by(PostORM.id.asc())
    
    post = db.execute(post_list).scalars().all()
    
    return post


@app.get("/posts/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="ID del post",
    description="Identificador entero del post. Debe ser mayor a 1",
   # example=1
), include_content: bool = Query(default=True, description="Incluir o no el contenido"),
   db: Session = Depends(get_db)
             ):    
    # post = buscar_post(post_id,db)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return PostPublic.model_validate(post,from_attributes=True) if include_content else PostSummary.model_validate(post,from_attributes=True)
    



@app.post("/posts", response_model=PostPublic, response_description="Post creado (OK)",status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate,db:Session= Depends(get_db)):
    author_obj = None
    if post.author:
        author_obj = db.execute(
            select(AuthorORM).where(AuthorORM.email == post.author.email)
        ).scalar_one_or_none()
        
        if not author_obj:
            author_obj = AuthorORM(name=post.author.name, email=post.author.email)
            db.add(author_obj)
            db.flush()  # Asegura que author_obj tenga un ID asignado
            
            
            
    new_post = PostORM(title=post.title,content=post.content, author=author_obj)
    for tag in post.tags:
        tag_obj = db.execute(
            select(TagORM).where(func.lower(TagORM.name) == tag.name.lower())
        ).scalar_one_or_none()
        
        if not tag_obj:
            tag_obj = TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()  # Asegura que tag_obj tenga un ID asignado
            
        new_post.tags.append(tag_obj)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El título del post ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post") 
    


@app.put("/posts/{post_id}", response_model=PostPublic, response_description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate,db:Session= Depends(get_db)):
    post = buscar_post(post_id,db)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    updates  = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(post, key, value)
        
    db.add(post)
    db.commit()
    db.refresh(post)
    return post     


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_description="Post eliminado")
def delete_post(post_id: int,db:Session= Depends(get_db)):    
    post = buscar_post(post_id,db)
    if post:
        db.delete(post)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Post no encontrado")
            
            
# def buscar_post(id:int,db:Session ) -> Optional[PostORM]:
#     stmt = select(PostORM).where(PostORM.id == id)
#     post = db.execute(stmt).scalar_one_or_none()
#     return post

