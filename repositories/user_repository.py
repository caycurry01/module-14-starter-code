from typing import Any, Dict, List
from repositories.db import get_pool
from psycopg.rows import dict_row

# Function to check if a username already exists in the database
def does_username_exist(username: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Using a parameterized query to prevent SQL injection
            cur.execute('SELECT user_id FROM app_user WHERE username = %s', [username])
            user_id = cur.fetchone()
            return user_id is not None

# Function to create a new user in the database
def create_user(username: str, password: str) -> Dict[str, Any]:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Using a parameterized query to prevent SQL injection
            cur.execute('''
                        INSERT INTO app_user (username, password)
                        VALUES (%s, %s)
                        RETURNING user_id
                        ''', [username, password])
            user_id = cur.fetchone()
            if user_id is None:
                raise Exception('Failed to create user')
            return {
                'user_id': user_id,
                'username': username
            }

# Function to retrieve a user by their username
def get_user_by_username(username: str) -> Dict[str, Any] | None:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Using a parameterized query to prevent SQL injection
            cur.execute('SELECT user_id, username, password AS hashed_password FROM app_user WHERE username = %s', [username])
            user = cur.fetchone()
            return user

# Function to retrieve a user by their user_id
def get_user_by_id(user_id: int) -> Dict[str, Any] | None:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Using a parameterized query to prevent SQL injection
            cur.execute('SELECT user_id, username FROM app_user WHERE user_id = %s', [user_id])
            user = cur.fetchone()
            return user

# Function to search for users based on a search query
def search_users(search_query: str) -> List[Dict[str, Any]]:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Using a parameterized query to prevent SQL injection
            cur.execute('SELECT user_id, username FROM app_user WHERE username LIKE %s', ['%' + search_query + '%'])
            users = cur.fetchall()
            return users
