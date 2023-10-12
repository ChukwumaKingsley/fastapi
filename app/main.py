from fastapi import FastAPI
from app import models
from app.database import engine
from .routers import user, post, auth, vote, downvote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware



# models.Base.metadata.create_all(bind=engine)

origins = ["*"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id":1}, {"title": "favourite foods", "content":"I like pizza","id":2}]

def find_post(id):
    # cursor.execute()
    for p in my_posts:
        if p["id"] == id:
            return p
def find_index_post(id):
    for p in my_posts:
        if p['id'] == id:
            return my_posts.index(p)
    return None

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(downvote.router)

@app.get("/")
def root():
    return {"message":"Welcome to my good api"}