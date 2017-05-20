CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  password CHARACTER(64) NOT NULL,
  login VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE auth_tokens (
  user_id INTEGER UNIQUE NOT NULL,
  token CHARACTER(64) NOT NULL,
  expiration_date TIMESTAMP NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE movies (
  movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(256) NOT NULL,
  release_year INTEGER NOT NULL,
  director VARCHAR(256) NOT NULL,
  language VARCHAR(64) NOT NULL,
  subtitles VARCHAR(64),
  age_restriction INTEGER,
  duration INTEGER NOT NULL,
  box_office VARCHAR(40),
  description TEXT,
  poster TEXT
);

CREATE TABLE reviews (
  movie_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  review TEXT,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  UNIQUE (movie_id, user_id)
);

CREATE TABLE seats (
  seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
  hall_no INTEGER NOT NULL,
  row_no INTEGER NOT NULL,
  seat_no INTEGER NOT NULL,
  special_features VARCHAR(32),
  UNIQUE(hall_no, row_no, seat_no)
);

CREATE TABLE sessions (
  session_id INTEGER PRIMARY KEY AUTOINCREMENT,
  movie_id INTEGER NOT NULL,
  begin_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  hall_no INTEGER NOT NULL,
  FOREIGN KEY(movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE tickets (
  user_id INTEGER,
  seat_id INTEGER NOT NULL,
  session_id INTEGER NOT NULL,
  amount MONEY NOT NULL,
  sold BOOLEAN NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id),
  UNIQUE (seat_id, session_id)
);