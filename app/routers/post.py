from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import String, case, desc, func, and_, literal
from sqlalchemy.sql import select
from .. import models, schemas, oauth2
from ..database import Session, get_db
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/")
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")
    is_creator = case(
        (models.Post.user_id == current_user.id, literal(True)),
        else_=literal(False)
    ).label("is_creator")
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_creator,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_creator': post.is_creator,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic
    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/my_posts")
def get_my_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.Post.user_id == current_user.id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic

    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/user_posts/{id}")
def get_user_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.Post.user_id == id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic
    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/my_votes")
def get_my_likes(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )


    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.Vote.user_id == current_user.id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic

    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/user_votes/{id}")
def get_user_likes(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.Vote.user_id == id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic

    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/my_downvotes")
def get_my_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.DownVote.user_id == current_user.id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic

    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/user_downvotes/{id}")
def get_user_likes(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    subquery_vote = case((func.count().filter(models.Vote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_voted")
    subquery_downvote = case((func.count().filter(models.DownVote.user_id == current_user.id) > 0, literal(True)), else_=literal(False)).label("user_downvoted")

    search_lower = search.lower()
    current_time = datetime.now()
    is_editable = case((
                    (current_time - models.Post.created_at) <= timedelta(minutes=30),
                    literal(True)),
                else_=literal(False)
            ).label("is_editable")
    subquery_profile_pic = (
        db.query(models.User.profile_pic)
        .filter(models.User.id == models.Post.user_id)
        .label("profile_pic")
    )

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
            func.count(models.Vote.post_id).label("votes"),
            func.count(models.DownVote.post_id).label("downvotes"),
            subquery_vote,
            subquery_downvote,
            is_editable,
            subquery_profile_pic
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .outerjoin(models.DownVote, models.DownVote.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.published == True, models.DownVote.user_id == id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'votes': post.votes,
        'downvotes': post.downvotes,
        'user_voted': post.user_voted,
        'user_downvoted': post.user_downvoted,
        'is_editable': post.is_editable,
        'profile_pic': post.profile_pic

    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.get("/drafts")
def get_drafts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):

    search_lower = search.lower()

    posts_query = (
        db.query(
            models.Post.id,
            models.Post.user_id,
            models.Post.user_name,
            models.Post.title,
            models.Post.content,
            func.cast(models.Post.created_at, String).label("created_at"),
        )
        .filter(models.Post.published == False, models.Post.user_id == current_user.id)
        .filter(func.lower(models.Post.title).contains(search_lower) | func.lower(models.Post.content).contains(search_lower))
        .order_by(desc(models.Post.created_at))
        .limit(limit)
        .offset(skip)
        .all()
    )

    def serialize_post(post):
        post_dict = {
        'id': post.id,
        'user_id': post.user_id,
        'user_name': post.user_name,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
    }
        return post_dict
    serialized_posts = [serialize_post(post) for post in posts_query]

    return JSONResponse(content=serialized_posts)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model = schemas.PostCreate)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == current_user.id).first()
    user_name = user_query.name 

    new_post = models.Post(**post.dict(), user_id = current_user.id, user_name = user_name)
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

