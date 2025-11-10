CREATE DATABASE testbudgettracker; 

USE testbudgettracker;


CREATE TABLE expenses (
    userID INT, 
    username VARCHAR(255), 
    transaction_id INT,
    expense_description VARCHAR(255), 
    amount INT,
    origin VARCHAR(255)
); 

CREATE TABLE money(
    userID INT, 
    username VARCHAR(255), 
    balance INT
);

CREATE TABLE scheduledpayments(
    userID INT, 
    username VARCHAR(255),
    scheduleid INT,
    paymentname VARCHAR(255),
    amount INT,
    duedate DATE
);

CREATE TABLE sessiontracker(
    userID INT, 
    username VARCHAR(255),
    useractive BOOLEAN  
);

CREATE TABLE users(
    userID INT, 
    username VARCHAR(255)
); 
