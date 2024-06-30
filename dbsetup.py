import mysql.connector
from datetime import datetime
from typing import List, Optional, Dict

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootdatabase24",
        database="mydb"
    )
    
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            UserID VARCHAR(255) PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            EmailAddress VARCHAR(255) NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `Group` (
            GroupID VARCHAR(255) PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Admin VARCHAR(255) NOT NULL,
            Description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GroupMember (
            GroupID VARCHAR(255),
            UserID VARCHAR(255),
            PRIMARY KEY (GroupID, UserID),
            FOREIGN KEY (GroupID) REFERENCES `Group` (GroupID),
            FOREIGN KEY (UserID) REFERENCES User (UserID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Expense (
            ExpenseID VARCHAR(255) PRIMARY KEY,
            GroupID VARCHAR(255) NOT NULL,
            PaidBy VARCHAR(255) NOT NULL,
            Amount DOUBLE NOT NULL,
            Timestamp DATETIME NOT NULL,
            Description TEXT,
            FOREIGN KEY (GroupID) REFERENCES `Group` (GroupID),
            FOREIGN KEY (PaidBy) REFERENCES User (UserID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ExpenseParticipants (
            ExpenseID VARCHAR(255),
            UserID VARCHAR(255),
            AmountShared DOUBLE NOT NULL,
            PRIMARY KEY (ExpenseID, UserID),
            FOREIGN KEY (ExpenseID) REFERENCES Expense (ExpenseID),
            FOREIGN KEY (UserID) REFERENCES User (UserID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            TransactionID VARCHAR(255) PRIMARY KEY,
            PaidBy VARCHAR(255) NOT NULL,
            PaidTo VARCHAR(255) NOT NULL,
            Amount DOUBLE NOT NULL,
            Method VARCHAR(255) NOT NULL,
            GroupID VARCHAR(255) NOT NULL,
            Timestamp DATETIME NOT NULL,
            FOREIGN KEY (PaidBy) REFERENCES User (UserID),
            FOREIGN KEY (PaidTo) REFERENCES User (UserID),
            FOREIGN KEY (GroupID) REFERENCES `Group` (GroupID)
        )
    """)
    
    conn.commit()
    return conn
