from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://192.168.64.12:30080",
    "http://localhost:30080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Post(BaseModel):
    id: int | None = None
    title: str
    content: str

POSTS: list[Post] = []
counter = 1


@app.get("/posts")
def list_posts():
    return POSTS


@app.post("/posts")
def create_post(post: Post):
    global counter
    post.id = counter
    counter += 1
    POSTS.append(post)
    return post


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    for idx, p in enumerate(POSTS):
        if p.id == post_id:
            post.id = post_id
            POSTS[idx] = post
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    global POSTS
    before = len(POSTS)
    POSTS = [p for p in POSTS if p.id != post_id]
    if len(POSTS) == before:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"ok": True}
