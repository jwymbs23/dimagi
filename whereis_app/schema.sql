DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS location;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  person_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE location (
  location_id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  location TEXT NOT NULL,
  lat DECIMAL  NOT NULL,
  lon DECIMAL NOT NULL,
  off_the_grid INTEGER DEFAULT 0,
  FOREIGN KEY (person_id) REFERENCES user (id)
);