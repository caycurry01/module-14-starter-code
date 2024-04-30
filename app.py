
import os
from flask import Flask, abort, redirect, render_template, request, session, url_for, jsonify
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit

from repositories import user_repository, message_repository
from repositories.db import get_pool

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
bcrypt = Bcrypt(app)

socketio = SocketIO(app) 

@app.get('/')
def index():
    if 'user_id' in session:
        return redirect('/secret')
    return render_template('index.html')


@app.get('/secret')
def secret_page():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session.get('user_id')
    user = user_repository.get_user_by_id(user_id)  # type: ignore
    return render_template('secret.html', user=user)


@app.post('/signup')
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        abort(400)
    does_user_exist = user_repository.does_username_exist(username)
    if does_user_exist:
        abort(400)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_repository.create_user(username, hashed_password)
    return redirect('/')


@app.post('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        abort(400)
    user = user_repository.get_user_by_username(username)
    if user is None:
        abort(401)
    if not bcrypt.check_password_hash(user['hashed_password'], password):
        abort(401)
    session['user_id'] = user['user_id']
    return redirect('/secret')


@app.post('/logout')
def logout():
    del session['user_id']
    return redirect('/')

@app.route('/messages')
def messages():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect('/')
    
    # Render messages.html template
    return render_template('messages.html')

# Add route to search for users
@app.route('/search_users', methods=['GET'])
def search_users():
    search_query = request.args.get('q', '')  # Get the search query from the URL parameter 'q'
    search_results = []  # Placeholder for search results

    # Perform search operation based on the search query (e.g., search for users with usernames similar to the search query)
    # Replace this with your actual search logic
    if search_query:
        search_results = user_repository.search_users(search_query)

    # Render search_users.html template with search results
    return render_template('search_users.html', search_results=search_results)

@app.route('/messages/<int:recipient_id>')
def view_messages(recipient_id):
    # Check if user is logged in
    if 'user_id' not in session:
        # Redirect to login page
        return redirect(url_for('login'))
    
    # Get the logged-in user's ID
    sender_id = session.get('user_id')

    # Get or create the thread ID for the conversation between the sender and recipient
    thread_id = message_repository.get_or_create_thread(sender_id, recipient_id)

    # Fetch messages for the specified thread ID
    messages = message_repository.get_messages_for_thread(thread_id)

    # Fetch user information for both the sender and recipient
    sender = user_repository.get_user_by_id(sender_id)
    recipient = user_repository.get_user_by_id(recipient_id)

    # Render template to display messages
    return render_template('view_messages.html', messages=messages, sender=sender, recipient=recipient)


@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on("user_join")
def handle_user_join(username):
    print(f"User {username} joined!")
    # You can store the user's connection information in the database
    # For example, you can update the user's status to 'online'
    update_user_status(username, 'online')

@socketio.on("new_message")
def handle_new_message(data):
    sender_id = session.get('user_id')  # Get sender's user ID from session
    recipient_id = data.get('recipient_id')
    message_content = data.get('message_content')

    # Determine the thread ID based on the sender and recipient
    thread_id = message_repository.get_thread_id(sender_id, recipient_id)

    # If the thread doesn't exist, create a new one
    if not thread_id:
        thread_id = message_repository.create_thread(sender_id, recipient_id)

    # Insert the new message into the database with the thread ID
    message_repository.create_message(thread_id, sender_id, recipient_id, message_content)

    # Broadcast the new message to all clients
    emit("receive_message", {"thread_id": thread_id, "sender_id": sender_id, "message_content": message_content}, broadcast=True)

    # Emit a receive_message event to the sender's socket to display the new message automatically
    emit("receive_message", {"thread_id": thread_id, "sender_id": sender_id, "message_content": message_content}, room=sender_id)

def update_user_status(username, status):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE app_user SET status = %s WHERE username = %s", (status, username))
            conn.commit()
            

if __name__ == '__main__':
    socketio.run(app)