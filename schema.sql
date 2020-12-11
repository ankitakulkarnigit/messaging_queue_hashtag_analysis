PRAGMA foreign_keys;
BEGIN TRANSACTION;

drop table if exists Users;
create table Users (
  username string primary key not null,
  email string not null,
  pass password not null
);

drop table if exists Followers;
create table Followers (
  username string,
  usernamefollowing string,
  foreign key (username) references Users (username),
  foreign key (usernamefollowing) references Users (username)
);

drop table if exists Tweets;
create table Tweets (
  username string not null,
  tweet string not null,
  time_stamp timestamp DEFAULT (DATETIME('now', 'localtime'))
);

insert into Users (username, email, pass) values ('ankita', 'ankita@gmail.com', '0b923db03c8718ad3b5d3a885442ff03');
insert into Users (username, email, pass) values('aditi', 'aditi@gmail.com', 'b589dfbf1c1c742de1ef73e77324310b');
insert into Users (username, email, pass) values('shraddha', 'shraddha@gmail.com', '174037c99c15ad0ec6f6ff755eb0e3a8');
insert into Users (username, email, pass) values('brian', 'Brian@gmail.com', '51f1599a923b58ca176e0ac5bf34ae8c');
insert into Users (username, email, pass) values('mark', 'Mark@gmail.com', 'd1af90699f2a2c983e6ccb7bee874414');
insert into Users (username, email, pass) values('Rick', 'Rick@gmail.com', '45af90699f62a2c988e6ccb7bee87789');

insert into Followers (username, usernamefollowing) values ('ankita', 'aditi');
insert into Followers (username, usernamefollowing) values ('aditi', 'shraddha');
insert into Followers (username, usernamefollowing) values ('shraddha', 'ankita');
insert into Followers (username, usernamefollowing) values ('ankita', 'shraddha');

insert into Tweets (username, tweet) values ('ankita', 'My First Tweet');
insert into Tweets (username, tweet) values ('aditi', 'Hurray');
insert into Tweets (username, tweet) values ('ankita', 'Hey you all!!');
INSERT INTO Tweets(username, tweet) VALUES('ankita', 'Meanwhile, at the R1 institution down the street... https://uci.edu/coronavirus/messages/200710-sanitizer-recall.php');
INSERT INTO Tweets(username, tweet) VALUES('ankita', 'FYI: https://www.levels.fyi/still-hiring/');
INSERT INTO Tweets(username, tweet) VALUES('aditi', 'Yes, the header file ends in .h. C++ is for masochists.');
INSERT INTO Tweets(username, tweet) VALUES('shraddha', 'If academia were a video game, then a 2.5 hour administrative meeting that votes to extend time 15 minutes is a fatality. FINISH HIM');
INSERT INTO Tweets(username, tweet) VALUES('brian', 'I keep seeing video from before COVID, of people not needing to mask or distance, and doing something like waiting in line at Burger King. YOU''RE WASTING IT!');
INSERT INTO Tweets(username, tweet) VALUES('mark', '#cpsc315 #engr190w NeurIPS is $25 for students and $100 for non-students this year! https://medium.com/@NeurIPSConf/neurips-registration-opens-soon-67111581de99');


COMMIT;
/*
PRAGMA foreign_keys=ON;

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id        INTEGER PRIMARY KEY,
    username  TEXT NOT NULL UNIQUE,
    email     TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL
);
INSERT INTO Users VALUES(1, 'ProfAvery', 'kavery@fullerton.edu', 'password');
INSERT INTO Users VALUES(2, 'KevinAWortman', 'kwortman@fullerton.edu', 'qwerty');
INSERT INTO Users VALUES(3, 'Beth_CSUF', 'beth.harnick.shapiro@fullerton.edu', 'secret');

DROP TABLE IF EXISTS Followers;
CREATE TABLE Followers (
    id            INTEGER PRIMARY KEY,
    follower_id   INTEGER NOT NULL,
    following_id  INTEGER NOT NULL,

    FOREIGN KEY(follower_id) REFERENCES users(id),
    FOREIGN KEY(following_id) REFERENCES users(id),
    UNIQUE(follower_id, following_id)
);
INSERT INTO Followers(follower_id, following_id) VALUES(1, 2);
INSERT INTO Followers(follower_id, following_id) VALUES(1, 3);
INSERT INTO Followers(follower_id, following_id) VALUES(2, 1);
INSERT INTO Followers(follower_id, following_id) VALUES(2, 3);
INSERT INTO Followers(follower_id, following_id) VALUES(3, 2);

DROP TABLE IF EXISTS Tweets;
CREATE TABLE Tweets (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    text        TEXT NOT NULL,
    timestamp   INTEGER DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO Tweets(user_id, text) VALUES(1, 'Meanwhile, at the R1 institution down the street... https://uci.edu/coronavirus/messages/200710-sanitizer-recall.php');
INSERT INTO Tweets(user_id, text) VALUES(1, 'FYI: https://www.levels.fyi/still-hiring/');
INSERT INTO Tweets(user_id, text) VALUES(1, 'Yes, the header file ends in .h. C++ is for masochists.');
INSERT INTO Tweets(user_id, text) VALUES(2, 'If academia were a video game, then a 2.5 hour administrative meeting that votes to extend time 15 minutes is a fatality. FINISH HIM');
INSERT INTO Tweets(user_id, text) VALUES(2, 'I keep seeing video from before COVID, of people not needing to mask or distance, and doing something like waiting in line at Burger King. YOU''RE WASTING IT!');
INSERT INTO Tweets(user_id, text) VALUES(3, '#cpsc315 #engr190w NeurIPS is $25 for students and $100 for non-students this year! https://medium.com/@NeurIPSConf/neurips-registration-opens-soon-67111581de99');

COMMIT;
*/