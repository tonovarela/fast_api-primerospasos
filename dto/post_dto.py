
from pydantic import BaseModel,Field, field_validator
from typing import Optional,List

from app.models.Author import Author
from app.models.Tag import Tag

class PostBase(BaseModel):    
    title: str = Field(
    ...,
    min_length=3,
    max_lenght=100,
    description="Titulo del post (minimo 3 caracteres  y maximo 100)",
    examples=["Mi primer post con FastAPI"]
    )
    content:  Optional[str] ="Contenido no disponible",
    tags: Optional[List[Tag]]= Field(default_factory=list) 
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
    title: Optional[str] = Field(None,min_length=3, max_length=100)
    content: Optional[str] =Field(
        min_length=10,
        description="Contenido pendiente",
        examples=["Este es un ejemplo del contenido pendiente"]
    )
