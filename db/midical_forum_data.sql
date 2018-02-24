BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `users` (
	`user_id`	INTEGER UNIQUE,
	`username`	TEXT UNIQUE,
	`reg_date`	INTEGER,
	`last_login`	INTEGER,
	`msg_count`	INTEGER,
	PRIMARY KEY(`user_id`)
);
CREATE TABLE IF NOT EXISTS `user_profile` (
	`user_id`	INTEGER,
	`user_type`	INTEGER,
	`firstname`	TEXT,
	`lastname`	TEXT,
	`work_address`	TEXT,
	`gender`	TEXT,
	`age`	TEXT,
	`email`	TEXT,
	`picture`	TEXT,
	`phone`	INTEGER,
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
	PRIMARY KEY(`user_type`)
);
CREATE TABLE IF NOT EXISTS `user_password` (
	`user_id`	INTEGER,
	`password_hash`	TEXT,
	PRIMARY KEY(`user_id`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS `patient_profile` (
	`user_id`	INTEGER,
	`user_type`	INTEGER,
	`home_address`	TEXT,
	`med_rec_id`	INTEGER,
	`height`	INTEGER,
	`weight`	INTEGER,
	PRIMARY KEY(`user_id`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
	FOREIGN KEY(`user_type`) REFERENCES `user_profile`(`user_type`),
	FOREIGN KEY(`med_rec_id`) REFERENCES `medical_records`(`med_rec_id`) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS `messages` (
	`message_id`	INTEGER UNIQUE,
	`user_id`	INTEGER,
	`username`	TEXT,
	`reply_to`	INTEGER,
	`title`	TEXT,
	`body`	TEXT,
	`views`	INTEGER,
	`timestamp`	INTEGER,
	PRIMARY KEY(`message_id`),
	FOREIGN KEY(`reply_to`) REFERENCES `messages`(`message_id`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
	FOREIGN KEY(`username`) REFERENCES `users`(`username`)
);
CREATE TABLE IF NOT EXISTS `medical_records` (
	`med_rec_id`	INTEGER UNIQUE,
	`user_id`	INTEGER,
	`disease_id`	INTEGER,
	`disease_name`	TEXT,
	`disease_infection`	INTEGER,
	`disease_level`	TEXT,
	PRIMARY KEY(`med_rec_id`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`),
	FOREIGN KEY(`disease_name`) REFERENCES `disease`(`disease_name`),
	FOREIGN KEY(`disease_id`) REFERENCES `disease`(`disease_id`)
);
CREATE TABLE IF NOT EXISTS `doctor_profile` (
	`user_id`	INTEGER,
	`user_type`	INTEGER,
	`speciality`	TEXT,
	`work_achievments`	TEXT,
	FOREIGN KEY(`user_type`) REFERENCES `user_profile`(`user_type`),
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
	PRIMARY KEY(`user_id`)
);
CREATE TABLE IF NOT EXISTS `disease` (
	`disease_id`	INTEGER UNIQUE,
	`disease_name`	TEXT,
	`description`	TEXT,
	`disease_degree`	TEXT,
	`image`	TEXT,
	PRIMARY KEY(`disease_id`)
);
CREATE TABLE IF NOT EXISTS `diagnosis` (
	`diagnosis_id`	INTEGER UNIQUE,
	`user_id`	INTEGER,
	`message_id`	INTEGER,
	`disease_id`	INTEGER,
	`diagnosis_description`	TEXT,
	`mark_as_solution`	TEXT,
	FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
	FOREIGN KEY(`disease_id`) REFERENCES `disease`(`disease_id`),
	PRIMARY KEY(`diagnosis_id`),
	FOREIGN KEY(`message_id`) REFERENCES `messages`(`message_id`) ON DELETE SET NULL
);
COMMIT;
