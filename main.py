from fastapi import FastAPI, Query

app = FastAPI(title="Mini blog")
BLOG_POST =[
    {"id":1,"title":"Hola desde FastAPI","content":"Mi primer post con FastAPI"},
    {"id":2,"title":"Segundo post","content":"Mi primer post con FastAPI1"},
    {"id":3,"title":"Tercer post","content":"Mi primer post con FastAPI2"},
    {"id":4,"title":"Cuarto post","content":"Mi primer post con FastAPI3"},
]


@app.get("/")
def home():
    return {'message': "Bienevidos a Fastapi"}

@app.get("/posts")
def get_posts(query: str = Query( default=None,description="Search query string")):
    if query:
        results =(post for post in BLOG_POST if query.lower() in post['title'].lower())
        return {"data":results,"query":query}
    
    return {"data":BLOG_POST,"query":query}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    post_found = next((post for post in BLOG_POST if post['id'] == post_id), None)
    if post_found:
        return {"data":post_found}
    return {"message":"Post not found"}