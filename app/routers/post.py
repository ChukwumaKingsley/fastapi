from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# @router.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
    # posts = db.query(models.Post).all()
    # return {"data":posts}

@router.get("/")
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # conn.commit()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
    return posts


@router.get("/my_posts")
def get_my_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    my_posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()

    return my_posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model = schemas.PostCreate)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts(title, content, published) VALUES (%s,%s, %s) returning * """,
    #                (post.title, post.content, post.publish))
    # post = cursor.fetchall()
    # conn.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    new_post = models.Post(**post.dict(), user_id = current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return post


@router.get("/{id}", response_model = schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # # post = find_post(id)
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """,f"{id}")
    # post = cursor.fetchall()

    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # delete_params = {
    #     'id' : id
    # }
    # delete_query = """ 
    #     DELETE FROM posts WHERE id = %(id)s returning *;
    # """
    # cursor.execute(delete_query, delete_params)
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()


    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'post with id {id} does not exists.')
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not authorized to perform requested action!')
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"post with id {id} was successfully deleted!"}

@router.put("/{id}", response_model = schemas.Post)
def update_posts(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # # UPDATE query parameters
    # update_params = {
    #     'title': post.title,
    #     'content': post.content,
    #     'published': post.publish,
    #     'id' : id
    # }
    # # Update query
    # update_query = """
    # UPDATE posts 
    # SET title = %(title)s,
    #     content = %(content)s,
    #     published = %(published)s
    #     WHERE id = %(id)s returning * 
    # """

    # cursor.execute(update_query, update_params)
    # post = cursor.fetchall()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'post with id {id} does not exists.')
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not authorized to perform requested action!')

    post_query.update(updated_post.dict(), synchronize_session = False)
    db.commit()
    return post_query.first()

