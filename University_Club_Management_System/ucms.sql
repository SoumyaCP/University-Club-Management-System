CREATE DATABASE UCMS;
USE UCMS;
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);
ALTER TABLE User ADD COLUMN user_type VARCHAR(20);

CREATE TABLE Profile (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    SRN VARCHAR(20),
    gender VARCHAR(10),
    email VARCHAR(100),
    DOB DATE,
    phone_no VARCHAR(15),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


CREATE TABLE Events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    event_name VARCHAR(255) NOT NULL,
    date_of_conduction DATE, 
    venue VARCHAR(255),
    building VARCHAR(255)
);


CREATE TABLE Event_Feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    eventname VARCHAR(255) NOT NULL,
    eventdate DATE NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Announcement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    date_posted DATETIME NOT NULL
);

CREATE TABLE Members (
    member_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(100),
    role VARCHAR(50)
);

