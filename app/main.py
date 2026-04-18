from fastapi import FastAPI
from app.routers import auth,posts,categories,tags
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(categories.router)
app.include_router(tags.router)