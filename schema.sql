CREATE TABLE app_user (
  user_id  SERIAL,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  PRIMARY KEY (user_id)
);

CREATE TABLE user_sessions (
  sid SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES app_user(user_id),
  session_id VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE message_threads (
  thread_id SERIAL PRIMARY KEY,
  sender_id INTEGER REFERENCES app_user(user_id),
  recipient_id INTEGER REFERENCES app_user(user_id),
  UNIQUE (sender_id, recipient_id)
);

CREATE TABLE messages (
  message_id SERIAL PRIMARY KEY,
  thread_id INTEGER REFERENCES message_threads(thread_id),
  sender_id INTEGER REFERENCES app_user(user_id),
  recipient_id INTEGER REFERENCES app_user(user_id),
  message_content TEXT,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CREATE TABLE message_threads (
--   thread_id SERIAL PRIMARY KEY,
--   user1_id INTEGER REFERENCES app_user(user_id),
--   user2_id INTEGER REFERENCES app_user(user_id),
--   UNIQUE (user1_id, user2_id)
-- );