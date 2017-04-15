CREATE TABLE users (
	user_id integer,
	password char(64),
	display_name varchar(32),
	PRIMARY KEY(user_id)
);

CREATE TABLE reviews (
	movie_id integer,
	user_id integer,
	rating integer,
	review text,
	PRIMARY KEY(movie_id, user_id)
);

CREATE TABLE movies (
	movie_id integer,
	poster bytea,
	title varchar(256),
	release_year integer,
	director varchar(256),
	language varchar(64),
	subtitles varchar(64),
	age_restriction integer,
	duration interval,
	box_office money,
	PRIMARY KEY(movie_id)
);

CREATE TABLE sessions (
	session_id integer,
	movie_id integer,
	begin_time timestamp,
	end_time timestamp,
	hall_no integer,
	PRIMARY KEY(session_id)
);

CREATE TABLE tickets (
	user_id integer,
	seat_id integer,
	session_id integer,
	PRIMARY KEY(user_id, seat_id, session_id)
);

CREATE TABLE seat_cost (
	seat_id integer,
	session_id integer,
	amount money,
	PRIMARY KEY(seat_id, session_id)
);

CREATE TABLE seats (
	seat_id integer,
	hall_no integer,
	row_no integer,
	seat_no integer,
	special_features varchar(32),
	PRIMARY KEY(seat_id)
);