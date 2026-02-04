
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy.orm import Session

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Path, Query,status
from typing import List, Literal, Optional, Union

from app.core.db import get_db
from .schemas import (PostPublic, PaginatedPost,PostCreate, PostUpdate,PostSummary)
from .repository import PostRespository
from app.core.security import oauth2_scheme,get_currrent_user


router = APIRouter(prefix="/posts", tags=["posts"])





@router.get("/", response_model=PaginatedPost)
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
    db: Session = Depends(get_db),
    user= Depends(get_currrent_user)
  ):
    repository = PostRespository(db)
    total ,items = repository.search(
        query=query or text,
        order_by=order_by,
        direction=direction,
        page=page,
        per_page=per_page
    )
    
    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)
    has_prev = page > 1
    has_next = page * per_page < total
    
    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages= total_pages,
        has_prev= has_prev,
        has_next= has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )
    
    
@router.get("/by-tags", response_model=List[PostPublic]) 
def get_posts_by_tags(
    tags: Optional[str] = Query(default=None,description="Lista de etiquetas separadas por comas",
                                # example="python,fastapi,sqlalchemy"
                                ),
    db: Session = Depends(get_db),
    user= Depends(get_currrent_user)
):
    repository = PostRespository(db)
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    posts = repository.by_tags(tag_list)    
    return posts


@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="ID del post",
    description="Identificador entero del post. Debe ser mayor a 1",
   # example=1
), include_content: bool = Query(default=True, description="Incluir o no el contenido"),
   db: Session = Depends(get_db),
   user= Depends(get_currrent_user)
             ):    
    repository = PostRespository(db)
    post = repository.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    return PostPublic.model_validate(post,from_attributes=True) if include_content else PostSummary.model_validate(post,from_attributes=True)


@router.post("/", response_model=PostPublic, response_description="Post creado (OK)",status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate,db:Session= Depends(get_db),user= Depends(get_currrent_user)):
    repository= PostRespository(db)    
    try:
        post =repository.create(title=post.title,
                                content=post.content,
                                tags=[tag.model_dump() for tag in post.tags],
                                author=(post.author.model_dump() if post.author else None)
                                )        
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError : 
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al crear el post") 
    except SQLAlchemyError :
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor al crear el post")
        


@router.put("/{post_id}", response_model=PostPublic, response_description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate,db:Session= Depends(get_db),user= Depends(get_currrent_user)):
    repository = PostRespository(db)
    post = repository.get(post_id=post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post no encontrado")
    updates  = data.model_dump(exclude_unset=True)
    repository.update(post=post,updates=updates)    
    db.commit()
    db.refresh(post)
    return post



@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_description="Post eliminado")
def delete_post(post_id: int,db:Session= Depends(get_db),user= Depends(get_currrent_user)): 
    repository = PostRespository(db)
    post = repository.get(post_id=post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post no encontrado")    
    repository.delete(post)
    db.delete(post)
    db.commit()
        

@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme),user= Depends(get_currrent_user)):
    
    return {"message": f"Token, {token}. Has accedido a un endpoint seguro."}    