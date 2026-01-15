from pydantic import BaseModel,Field,field_validator
from typing import Optional


class Author(BaseModel):
    name:str = Field(...,min_length=2,max_length=30,description="Nombre del author")
    email:Optional[str] ="sin correo"    
    @field_validator("email")
    @classmethod
    def validate_email(cls,value:str)->str:        
        if ("@" not in value and "." not in value ):
            raise ValueError(f"Esto no parece un correo electronico")                                
        return value
    