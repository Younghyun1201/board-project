from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# -------------------
# DB 설정 (MySQL)
# -------------------
# 서비스 이름: board-mysql (같은 namespace: board)
# DB 이름: board
# 계정: root / 비밀번호: root
DATABASE_URL = "mysql+pymysql://root:root@board-mysql:3306/board"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)


# 테이블 자동 생성 (처음 한 번)
Base.metadata.create_all(bind=engine)

# -------------------
# FastAPI 설정
# -------------------

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

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/posts", response_model=list[Post])
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).order_by(PostModel.id.desc()).all()
    return posts


@app.post("/posts", response_model=Post)
def create_post(post: Post, db: Session = Depends(get_db)):
    obj = PostModel(title=post.title, content=post.content)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, post: Post, db: Session = Depends(get_db)):
    obj = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")

    obj.title = post.title
    obj.content = post.content
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    obj = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(obj)
    db.commit()
    return {"ok": True}
