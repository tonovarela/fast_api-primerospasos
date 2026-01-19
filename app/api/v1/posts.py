from typing import List, Union,Optional

from fastapi import APIRouter, HTTPException, Query,Path

from dto.post_dto import PostCreate, PostUpdate
from response.response import (
    PostCreateResponse,
    PostUpdateResponse,
    PostSummaryResponse,
    PostResponse,
)

router = APIRouter(prefix="/posts", tags=["posts"])

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "content": "Mi primer post con FastAPI"},
    {"id": 2, "title": "Segundo post", "content": "Mi primer post con FastAPI1"},
    {"id": 3, "title": "Tercer post", "content": "Mi primer post con FastAPI2"},
    {"id": 4, "title": "Cuarto post", "content": "Mi primer post con FastAPI3"},
]


@router.get("/", response_model=List[PostResponse])
def get_posts(query: Optional[str] = Query(
    default=None, 
    description="Search query string",
    alias="search",
    min_length=3,
    max_length=50,
    pattern="^[^\W\d_]+$"
    
    )):
    if query:
        results = (
            post for post in BLOG_POST if query.lower() in post["title"].lower()
        )
        return list(results)
    return BLOG_POST


@router.get(
    "/{post_id}",
    response_model=Union[PostResponse, PostSummaryResponse],
    response_description="Post encontrado",
)
def get_post(
    post_id: int =Path(
        ...,
        title="ID del post",
        description="El ID del post que quieres obtener",
        ge=1,
        example=1,
        ),
    include_content: bool = Query(default=False, description="With content"),
):
    post_found = next((post for post in BLOG_POST if post["id"] == post_id), None)
    if post_found:
        if not include_content:
            id_, title = post_found["id"], post_found["title"]
            return {
                "id": id_,
                "title": title,
                "autor": post_found.get("autor"),
                "tags": [getattr(tag, "model_dump", lambda: tag)() for tag in post_found.get("tags", [])],
            }
        return post_found
    raise HTTPException(status_code=404, detail="Post no encontrado")


@router.post("/", response_model=PostCreateResponse)
def create_post(post: PostCreate):
    new_id = (BLOG_POST[-1]["id"]) + 1 if BLOG_POST else 1

    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "tags": post.tags,
        "autor": post.autor,
    }

    BLOG_POST.append(new_post)
    return {"message": "Post creado", "data": new_post}


@router.put("/{post_id}", response_model=PostUpdateResponse)
def update_post(post_id: int, post: PostUpdate):
    post_found = next((post for post in BLOG_POST if post["id"] == post_id), None)
    if not post_found:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    payload = post.model_dump(exclude_unset=True)
    if "title" in payload:
        post_found["title"] = payload["title"]
    if "content" in payload:
        post_found["content"] = payload["content"]

    return {"message": "Post actualizado", "post": post_found}


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return {"message": "Post borrado"}
    raise HTTPException(status_code=404, detail="Post no encontrado")
