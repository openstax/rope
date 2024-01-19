from fastapi import FastAPI

app = FastAPI(title="ROPE API", root_path="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}
