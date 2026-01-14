from fastapi import FastAPI

app = FastAPI(title="Mini block")


@app.get("/")
def home():
    print("Hola mundo")
    return {'message': "Bienevidos a Minibloc"}