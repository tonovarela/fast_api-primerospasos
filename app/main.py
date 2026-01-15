from fastapi import FastAPI

from app.api.v1.posts import router as posts_router

app = FastAPI(title="Blog")


@app.get("/")
def home():
    return {"message": "Bienvenidos a FastAPI"}


app.include_router(posts_router)
