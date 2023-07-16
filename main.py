from fastapi import Depends, FastAPI
from src.routers import users_router as users
import uvicorn

app = FastAPI()


app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health")
async def root():
    return {"message": "ok"}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
