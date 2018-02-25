PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users_profile (
	user_id	INTEGER,
	user_type	INTEGER NOT NULL,
	firstname	TEXT NOT NULL,
	lastname	TEXT NOT NULL,
	work_address	TEXT NOT NULL,
	gender	TEXT NOT NULL,
	age	TEXT NOT NULL,
	email	TEXT NOT NULL,
	picture	TEXT,
	phone	INTEGER,
	diagnosis_id	INTEGER,
	height	INTEGER,
	weight	INTEGER,
	speciality	TEXT,
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL,
	PRIMARY KEY(user_id),
	FOREIGN KEY(diagnosis_id) REFERENCES diagnosis(diagnosis_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS users (
	user_id	INTEGER UNIQUE,
	username	TEXT NOT NULL UNIQUE,
	pass_hash	TEXT NOT NULL,
	reg_date	INTEGER,
	last_login	INTEGER,
	msg_count	INTEGER,
	PRIMARY KEY(user_id)
);
CREATE TABLE IF NOT EXISTS messages (
	message_id	INTEGER,
	user_id	INTEGER NOT NULL,
	username	TEXT NOT NULL,
	reply_to	INTEGER,
	title	TEXT,
	body	TEXT,
	views	INTEGER,
	timestamp	INTEGER,
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY(reply_to) REFERENCES messages(message_id) ON DELETE CASCADE,
	PRIMARY KEY(message_id)
);
CREATE TABLE IF NOT EXISTS diagnosis (
	diagnosis_id	INTEGER,
	user_id	INTEGER NOT NULL,
	message_id	INTEGER NOT NULL,
	disease	TEXT,
	diagnosis_description	TEXT,
	PRIMARY KEY(diagnosis_id),
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY(message_id) REFERENCES messages(message_id) ON DELETE CASCADE
);
COMMIT;
PRAGMA foreign_keys=ON;