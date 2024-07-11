CREATE database IF NOT EXISTS bill_sharing_app;
USE bill_sharing_app;
CREATE TABLE IF NOT EXISTS Users (
  user_id VARCHAR(128) NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  created DATETIME NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE KEY email (email)
);

CREATE TABLE IF NOT EXISTS GroupDetails (
  group_id VARCHAR(128) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(255),
  admin_id VARCHAR(128) NOT NULL,
  created DATETIME NOT NULL,
  PRIMARY KEY (group_id),
  FOREIGN KEY (admin_id) REFERENCES Users(user_id),
  KEY admin_id (admin_id),
  KEY name (name)
);

CREATE TABLE IF NOT EXISTS Expenses (
  expense_id VARCHAR(128) NOT NULL,
  group_id VARCHAR(128) NOT NULL,
  description TINYTEXT,
  tag VARCHAR(255),
  timestamp DATETIME NOT NULL,
  paid_by VARCHAR(128) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (expense_id),
  FOREIGN KEY (paid_by) REFERENCES Users(user_id),
  FOREIGN KEY (group_id) REFERENCES GroupDetails(group_id),
  KEY group_id (group_id),
  KEY paid_by (paid_by)
);

CREATE TABLE IF NOT EXISTS Transactions (
  trans_id VARCHAR(128) NOT NULL,
  expense_id VARCHAR(128) NOT NULL,
  payer_id VARCHAR(128) NOT NULL,
  payee_id VARCHAR(128) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  timestamp DATETIME NOT NULL,
  PRIMARY KEY (trans_id),
  FOREIGN KEY (payee_id) REFERENCES Users(user_id),
  FOREIGN KEY (payer_id) REFERENCES Users(user_id),
  FOREIGN KEY (expense_id) REFERENCES Expenses(expense_id),
  KEY expense_id (expense_id),
  KEY payer_id (payer_id),
  KEY payee_id (payee_id)
);

CREATE TABLE IF NOT EXISTS GroupMembers (
  user_id VARCHAR(128) NOT NULL,
  group_id VARCHAR(128) NOT NULL,
  PRIMARY KEY (user_id, group_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (group_id) REFERENCES GroupDetails(group_id)
);

CREATE TABLE IF NOT EXISTS ExpenseParticipants (
  expense_id VARCHAR(128) NOT NULL,
  user_id VARCHAR(128) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  settled ENUM('SETTLED', 'PARTIAL', 'NO') NOT NULL,
  PRIMARY KEY (expense_id, user_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (expense_id) REFERENCES Expenses(expense_id),
  KEY amount (amount),
  KEY settled (settled)
);
