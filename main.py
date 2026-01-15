from fastapi import FastAPI, Query,Body,HTTPException

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
def get_post(post_id: int,include_content:bool= Query(default=False,description="With content")):
    post_found = next((post for post in BLOG_POST if post['id'] == post_id), None)        
    if post_found:                            
        if not include_content:
            id_, title = post_found["id"], post_found["title"]
            return {"data":{ "id":id_,"title":title}}            
        return {"data":post_found}                     
    raise HTTPException(status_code=404, detail="Post no encontrado")


@app.post("/posts")
def create_post(post:dict =Body(...)):
    print(post)
    if "title" not in post or "content" not in post:        
        raise HTTPException(status_code=400, detail="Title y Content son requeridos")
    if not str(post["title"]).strip():
        raise HTTPException(status_code=400, detail="Title no puede estar vacio")  
    new_id = (BLOG_POST[-1]["id"])+1 if BLOG_POST else 1
    
    new_post= {"id":new_id,
               "title":post["title"],
               "content":post["content"]
               }
    BLOG_POST.append(new_post)
    return {
        "message":"Post creado",
        "data":new_post
        
    }
  
  
@app.put("/posts/{post_id}")
def update_post(post_id:int, post:dict=Body(...)):
    post_found = next((post for post in BLOG_POST if post['id'] == post_id), None)        
    if not post_found:
        raise HTTPException(status_code=404, detail="Post no encontrado")    
    if "title" in post:
        if not str(post["title"]).strip():
            raise HTTPException(status_code=400, detail="Title no puede estar vacio")  
        post_found["title"]=post["title"]
    if "content" in post:
        post_found["content"]=post["content"]
    return {
        "message":"Post actualizado",
        "data":post_found        
    }  
    
    
@app.delete("/posts/{post_id}")
def delete_post(post_id:int):
    for index,post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return  {"message":"Post borrado"}
    raise HTTPException(status_code=404,detail="Post no encontrado")    