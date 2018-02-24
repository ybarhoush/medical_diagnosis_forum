BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users_profile (
	user_id	INTEGER,
	user_type	INTEGER,
	firstname	TEXT,
	lastname	TEXT,
	work_address	TEXT,
	gender	TEXT,
	age	TEXT,
	email	TEXT,
	picture	TEXT,
	phone	INTEGER,
	diagnosis_id	INTEGER,
	height	INTEGER,
	weight	INTEGER,
	speciality	TEXT,
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL,
	FOREIGN KEY(diagnosis_id) REFERENCES diagnosis(diagnosis_id) ON DELETE SET NULL,
	PRIMARY KEY(user_type)
);
CREATE TABLE IF NOT EXISTS users (
	user_id	INTEGER UNIQUE,
	username	TEXT UNIQUE,
	pass_hash	TEXT,
	reg_date	INTEGER,
	last_login	INTEGER,
	msg_count	INTEGER,
	PRIMARY KEY(user_id)
);
CREATE TABLE IF NOT EXISTS messages (
	message_id	INTEGER UNIQUE,
	user_id	INTEGER,
	username	TEXT,
	reply_to	REAL,
	title	TEXT,
	body	TEXT,
	views	INTEGER,
	timestamp	INTEGER,
	PRIMARY KEY(message_id),
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY(username) REFERENCES users(username),
	FOREIGN KEY(reply_to) REFERENCES messages(message_id)
);
CREATE TABLE IF NOT EXISTS diagnosis (
	diagnosis_id	INTEGER UNIQUE,
	user_id	INTEGER,
	message_id	INTEGER,
	disease	TEXT,
	diagnosis_description	TEXT,
	PRIMARY KEY(diagnosis_id),
	FOREIGN KEY(message_id) REFERENCES messages(message_id) ON DELETE SET NULL,
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
);
COMMIT;
