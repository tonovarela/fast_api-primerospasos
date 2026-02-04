
from fastapi import FastAPI 
from dotenv import load_dotenv
from app.core.db import Base,engine
from app.api.v1.posts.router import router as posts_router
from app.api.v1.auth.router import router as auth_router
# import logging
# logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)



load_dotenv()

   
def create_app()->FastAPI:
    app = FastAPI(title="Miniblog")
    Base.metadata.create_all(bind=engine)    
    app.include_router(auth_router,prefix="/api/v1")
    app.include_router(posts_router)
    
    
    return app

app = create_app()




    
    
    


