from fastapi import FastAPI, Query , HTTPException
from pydantic import BaseModel,Field, field_validator
from typing import Optional,List,Union

app = FastAPI(title="Blog")
BLOG_POST =[
    {"id":1,"title":"Hola desde FastAPI","content":"Mi primer post con FastAPI"},
    {"id":2,"title":"Segundo post","content":"Mi primer post con FastAPI1"},
    {"id":3,"title":"Tercer post","content":"Mi primer post con FastAPI2"},
    {"id":4,"title":"Cuarto post","content":"Mi primer post con FastAPI3"},
]

class Tag(BaseModel):
    name:str = Field(...,min_length=2,max_length=30,description="Nombre de la etiqueta")
    
class Author(BaseModel):
    name:str = Field(...,min_length=2,max_length=30,description="Nombre del author")
    email:Optional[str] ="sin correo"    
    @field_validator("email")
    @classmethod
    def validate_email(cls,value:str)->str:        
        if ("@" not in value and "." not in value ):
            raise ValueError(f"Esto no parece un correo electronico")                                
        return value
    
        
class PostBase(BaseModel):    
    title: str = Field(
    ...,
    min_length=3,
    max_lenght=100,
    description="Titulo del post (minimo 3 caracteres  y maximo 100)",
    examples=["Mi primer post con FastAPI"]
    )
    content:  Optional[str] ="Contenido no disponible",
    tags: Optional[List[Tag]]= [] 
    autor:Optional[Author] = None
    
class PostCreate(PostBase):
    title: str   = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (minimo 3 caracteres  y maximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: Optional[str] =Field(
        min_length=10,
        description="Contenido pendiente",
        examples=["Este es un ejemplo del contenido pendiente"]
    )        
    
    @field_validator("title")
    @classmethod
    def validate_title(cls,value:str)->str:        
        words_not_allowed = ["spam","lento","hola"]
        for word in words_not_allowed:            
            if word in value.lower():
                raise ValueError(f"El titulo no puede contener la palabra {word}")
        return value
    
class PostUpdate(BaseModel):
    title: str   = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (minimo 3 caracteres  y maximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: Optional[str] =Field(
        min_length=10,
        description="Contenido pendiente",
        examples=["Este es un ejemplo del contenido pendiente"]
    )




class PostResponse(PostBase):
    id:int    
    content:str
    
class PostSummaryResponse(BaseModel):
    id:int    
    title:str
        
class PostCreateResponse(BaseModel):
    message:str
    data:PostBase    

class PostUpdateResponse(PostCreateResponse):
    pass




@app.get("/")
def home():
    return {'message': "Bienvenidos a FastAPI"}


@app.get("/posts",response_model=List[PostResponse],)
def get_posts(query: str = Query( default=None,description="Search query string")):
    if query:
        results =(post for post in BLOG_POST if query.lower() in post['title'].lower())
        return results     
    return BLOG_POST


@app.get("/posts/{post_id}",response_model=Union[PostResponse,PostSummaryResponse],response_description="Post encontrado")
def get_post(post_id: int,include_content:bool= Query(default=False,description="With content")):
    post_found = next((post for post in BLOG_POST if post['id'] == post_id), None)        
    if post_found:                            
        if not include_content:
            id_, title = post_found["id"], post_found["title"]
            return { "id":id_,"title":title,"autor":post_found["autor"],"tags":[ tag.model_dump() for tag in post_found.tags]}
        return post_found                    
    raise HTTPException(status_code=404, detail="Post no encontrado")


@app.post("/posts",response_model=PostCreateResponse)
def create_post(post:PostCreate):     
    new_id = (BLOG_POST[-1]["id"])+1 if BLOG_POST else 1    
    
    new_post= {"id":new_id,
               "title":post.title,
               "content":post.content,
               "tags":post.tags,
               "autor":post.autor
               }
    
    BLOG_POST.append(new_post)
    return { "message":"Post creado","data":new_post}
  
  
@app.put("/posts/{post_id}",response_model=PostUpdateResponse)
def update_post(post_id:int, post:PostUpdate):
    post_found = next((post for post in BLOG_POST if post['id'] == post_id), None)        
    if not post_found:
        raise HTTPException(status_code=404, detail="Post no encontrado")    
    
    payload = post.model_dump(exclude_unset=True)
    if "title" in payload: post_found["title"] = payload["title"]
    if "content" in payload: post_found["content"] = payload["content"]
            
    return {  "message":"Post actualizado",
                "post":post_found
           }  
    
    
    
@app.delete("/posts/{post_id}",status_code=204)
def delete_post(post_id:int):    
    for index,post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return  {"message":"Post borrado"}
    raise HTTPException(status_code=404,detail="Post no encontrado")    





