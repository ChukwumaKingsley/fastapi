from typing import Optional
from fastapi import FastAPI, HTTPException, Response, responses, status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    publish: bool = True

while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', port = 5432, user = 'postgres',
                            password = 'domKing', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as Error:
        print("Connecting to database failed!")
        print("Error: ", Error)
        time.sleep(2)


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

@app.get("/")
def root():
    return {"message": "Welcome to my api"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    conn.commit()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(""" INSERT INTO posts(title, content, published) VALUES (%s,%s, %s) returning * """,
                   (post.title, post.content, post.publish))
    post = cursor.fetchall()
    conn.commit()
    return {"data": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    # post = find_post(id)
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """,f"{id}")
    post = cursor.fetchall()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    delete_params = {
        'id' : id
    }
    delete_query = """ 
        DELETE FROM posts WHERE id = %(id)s returning *;
    """
    cursor.execute(delete_query, delete_params)
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'post with id {id} does not exists.')
    return {"message": f"post with id {id} was successfully deleted!"}

@app.put("/posts/{id}")
def update_posts(id: int, post: Post):
    # UPDATE query parameters
    update_params = {
        'title': post.title,
        'content': post.content,
        'published': post.publish,
        'id' : id
    }
    # Update query
    update_query = """
    UPDATE posts 
    SET title = %(title)s,
        content = %(content)s,
        published = %(published)s
        WHERE id = %(id)s returning * 
    """

    cursor.execute(update_query, update_params)
    post = cursor.fetchall()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'post with id {id} does not exists.')

    return {"message": f"updated post with id {id}"}