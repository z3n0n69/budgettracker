CREATE DATABASE testbudgettracker; 

USE testbudgettracker;


CREATE TABLE expenses (
    userID INT, 
    username VARCHAR(255), 
    transaction_id INT,
    expense_description VARCHAR(255), 
    amount INT
); 

CREATE TABLE MONEY(
    userID INT, 
    username VARCHAR(255), 
    balance INT
);

CREATE TABLE scheduledpayments(
    userID INT, 
    username VARCHAR(255), 
    balance INT 
);

CREATE TABLE sessiontracker(
    userID INT, 
    username VARCHAR(255),
    useractive BOOLEAN  
);

CREATE TABLE users(
    userID INT, 
    username VARCHAR(255)
)
