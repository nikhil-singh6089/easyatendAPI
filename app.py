from fastapi import FastAPI
import uvicorn

test = FastAPI()

@test.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(test, host="127.0.0.1", port=8000)