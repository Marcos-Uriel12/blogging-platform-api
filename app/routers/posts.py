from fastapi import APIRouter, Depends, HTTPException
from requests import post
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Post, Category, Tag, PostTag
from app.utils import get_current_user
from app.models.models import User
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from math import ceil

router = APIRouter(prefix="/posts", tags=["posts"])

class PostCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[list[int]] = []

class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    tags: Optional[list[TagResponse]] = []

    class Config:
        from_attributes = True
        
@router.post("/", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category_id = post.category_id if post.category_id and post.category_id > 0 else None
    new_post = Post(
        title=post.title,
        content=post.content,
        category_id=category_id,
        user_id=current_user.id
    )
    db.add(new_post)
    db.flush()

    for tag_id in post.tags:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            db.add(PostTag(post_id=new_post.id, tag_id=tag_id))

    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/")
def get_posts(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    total = db.query(Post).count()
    offset = (page - 1) * limit
    posts = db.query(Post).offset(offset).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": ceil(total / limit),
        "data": [PostResponse.model_validate(post) for post in posts]
    }

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    category_id = post.category_id if post.category_id and post.category_id > 0 else None
    
    if post.title is not None and post.title != "":
        db_post.title = post.title
    if post.content is not None and post.content != "":
        db_post.content = post.content
    if post.category_id is not None and post.category_id != 0:
        db_post.category_id = post.category_id

    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_post)
    db.commit()
    
@router.patch("/{post_id}/publish", response_model=PostResponse)
def publish_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_post.status = "published"
    db.commit()
    db.refresh(db_post)
    return db_post


@router.post("/{post_id}/tags/{tag_id}", status_code=201)
def add_tag_to_post(post_id: int, tag_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    existing = db.query(PostTag).filter(PostTag.post_id == post_id, PostTag.tag_id == tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already added to this post")
    
    db.add(PostTag(post_id=post_id, tag_id=tag_id))
    db.commit()
    return {"message": "Tag added"}

@router.delete("/{post_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_post(post_id: int, tag_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post_tag = db.query(PostTag).filter(PostTag.post_id == post_id, PostTag.tag_id == tag_id).first()
    if not post_tag:
        raise HTTPException(status_code=404, detail="Tag not found on this post")
    
    db.delete(post_tag)
    db.commit()
