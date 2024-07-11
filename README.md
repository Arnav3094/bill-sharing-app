# Software Requirements Documentation

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to define the software requirements for a bill-sharing web application similar to Splitwise. This document outlines the functionalities, interfaces, and constraints of the system.

### 1.2 Scope

This document covers the requirements for developing a web-based application that allows users to share and manage expenses within groups or directly between individuals. It includes features such as user registration, expense management, notifications, and reporting.

### 1.3 Definitions, Acronyms, and Abbreviations

- SRD: Software Requirements Document
- UI: User Interface
- API: Application Programming Interface

### 1.4 References

## 2. Overall Description

### 2.1 Product Perspective

This application is intended to be a standalone web-based solution for managing shared expenses among individuals and groups. It aims to simplify the process of splitting bills and settling expenses.

### 2.2 Product Functions

#### Phase 1: Building Business Logic

The primary focus of this phase to set up the backend side logic.

Primary Features:
- User Registration and Login
- Group Creation and Management
- Expense Adding and Sharing
- Expense Settlement
- Report Generation
  
#### Phase 2: Building UI and Extra Features

Some of the Features in the pipeline are:
- Build the frontend and work on the UI
- Building API to connect the backend to the frontend
- Notifications and Reminders
- Dashboard and Reporting

### 2.3 Operating Environment

The application will run on modern web browsers (Chrome, Firefox, Safari, Edge) and be accessible on both desktop and mobile devices.

### 2.4 Assumptions and Dependencies

- Users will have internet access.
- Users will have a basic understanding of web applications.

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Phase 1:

##### 3.1.1.1 User Registration and Login

- Users can register using an email address and password.
- Users can log in using their registered credentials.

##### 3.1.1.2 Creating and Managing Groups

- Users can create groups and add members by email.
- Users can edit group details (name, description).

##### 3.1.1.3 Adding and Managing Expenses

- Users can add expenses with details such as amount, date, and description.
- Users can specify participants for the expense and split amounts unevenly (e.g., 30% for Person A, 50% for Person B).
- Users can edit or delete expenses.

##### 3.1.1.4 Clearing Expenses and Transactions

- Users can record payments made to settle expenses.
- Users can view outstanding balances with other users and groups.
- Users can record offline payments.

##### 3.1.1.5 Expense Categories

- Users can categorize expenses (e.g., food, travel, utilities).
- Users can filter expenses by category.

##### 3.1.1.6 Recurring Expenses

- Users can set up recurring expenses (e.g., monthly rent).

##### 3.1.1.7 Search and Filter

- Users can search for specific expenses or transactions.
- Users can filter expenses by date, category, or participant.

#### 3.1.1.9 Audit Log

- The system tracks all changes and transactions for transparency.
- Users can view a log of all activities related to their account.

##### 3.1.1.10 Report Generation
- Users can generate reports to determine the split between group members to make settling up offline easy
- The report will contain information about the sum owed by different users to each other

#### 3.1.2 Phase 2: Extra Features and UI

##### 3.1.2.1 Password recovery option via email.  

##### 3.1.2.2 Group admins can remove members and manage group settings.

##### 3.1.2.3 Users receive reminders for upcoming recurring expenses.

##### 3.1.2. Dashboard *(LATER)*

- Users can see an overview of all expenses, balances, and group activities.
- Users can view recent transactions and pending settlements.

##### 3.1.6 Notifications *(LATER)*

- Users receive email and/or push notifications for new expenses, payments, and reminders.
- Users can manage notification preferences.

##### 3.1.9 Expense Notes and Attachments *(LATER)*

- Users can add notes to expenses for additional details.
- Users can attach receipts or images to expenses.

##### 3.1.10 Currency Support *(LATER)*

- Users can add expenses in different currencies.
- The system will convert and display expenses in a common currency based on exchange rates.

##### 3.1.11 Expense Report Generation *(LATER)*

- Users can generate summary reports for individual or group expenses over a specified period.
- Reports can be exported as PDF or Excel files.

##### 3.1.13 User Profile Management *(LATER)*

- Users can update their profile details, including name, email, and profile picture.
- Users can change their password and manage account settings.


### 3.2 Non-Functional Requirements

#### 3.2.1 Performance Requirements

- The system should handle up to 500 concurrent users.
- The average page load time should be under 5 seconds.

#### 3.2.2 Safety Requirements

- The system should handle data securely, complying with data protection regulations.

#### 3.2.3 Security Requirements

- User data must be encrypted both in transit and at rest.
- Implement multi-factor authentication for added security.

#### 3.2.4 Business Rules

- Users must agree to the terms and conditions during registration.

## 4. External Interface Requirements

### 4.1 User Interfaces

The UI should be intuitive and user-friendly, with a clean and responsive design.

### 4.2 Hardware Interfaces

No specific hardware interfaces are required beyond a device capable of running a modern web browser.

### 4.3 Software Interfaces

- The system will interact with payment gateways for transaction processing.
- The system will use APIs for currency conversion rates.

### 4.4 Communication Interfaces

The system will use HTTPS for secure communication between the client and server.

## 5. API Specifications

### 5.1 User Management

`POST /api/register`

Description: Register a new user.

Request:

```json
{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "John Doe"
}
```

Response:

```json
{
    "success": true,
    "message": "User registered successfully"
}
```

`POST /api/login`

Description: Authenticate a user and generate a token.

Request:

```json

{
    "email": "user@example.com",
    "password": "securepassword"
}
```

Response:

```json
{
  "success": true,
  "token": "jwt-token"
}
```

`POST /api/password-recovery`

Description: Initiate password recovery process.

Request:

```json
{
  "email": "user@example.com"
}
```

Response:


```json
{
    "success": true,
    "message": "Password recovery email sent"
}
```

### 6.2 Group Management

`POST /api/groups`

Description: Create a new group.

Request:

```json
{
  "name": "Vacation Trip",
  "description": "Trip to Hawaii"
}
```

Response:

```json
{
  "success": true,
  "groupId": "group-id"
}
```

`GET /api/groups/{groupId}`

Description: Get details of a specific group.

Response:

```json
{
  "groupId": "group-id",
  "name": "Vacation Trip",
  "description": "Trip to Hawaii",
  "members": ["user-id-1", "user-id-2"]
}
```

`PUT /api/groups/{groupId}`

Description: Update group details.

Request:

```json
{
  "name": "New Group Name",
  "description": "Updated description"
}
```

Response:

```json
{
  "success": true,
  "message": "Group updated successfully"
}
```

`DELETE /api/groups/{groupId}`

Description: Delete a group.

Response:

```json
{
  "success": true,
  "message": "Group deleted successfully"
}
```

`POST /api/groups/{groupId}/members`

Description: Add a member to a group.

Request:

```json
{
    "email": "newmember@example.com"
}
```

Response:

json

Copy code

{

  "success": true,

  "message": "Member added successfully"

}

6\.3 Expense Management

POST /api/expenses

Description: Add a new expense.

Request:

json

Copy code

{

  "groupId": "group-id",

  "description": "Dinner at restaurant",

  "amount": 100.0,

  "date": "2023-01-01",

  "participants": [

    { "userId": "user-id-1", "share": 50.0 },

    { "userId": "user-id-2", "share": 50.0 }

  ]

}

Response:

json

Copy code

{

  "success": true,

  "expenseId": "expense-id"

}

GET /api/expenses/{expenseId}

Description: Get details of a specific expense.

Response:

json

Copy code

{

  "expenseId": "expense-id",

  "groupId": "group-id",

  "description": "Dinner at restaurant",

  "amount": 100.0,

  "date": "2023-01-01",

  "participants": [

    { "userId": "user-id-1", "share": 50.0 },

    { "userId": "user-id-2", "share": 50.0 }

  ]

}

PUT /api/expenses/{expenseId}

Description: Update an expense.

Request:

json

Copy code

{

  "description": "Updated description",

  "amount": 120.0,

  "date": "2023-01-02",

  "participants": [

    { "userId": "user-id-1", "share": 60.0 },

    { "userId": "user-id-2", "share": 60.0 }

  ]

}

Response:

json

Copy code

{

  "success": true,

  "message": "Expense updated successfully"

}

DELETE /api/expenses/{expenseId}

Description: Delete an expense.

Response:

json

Copy code

{

  "success": true,

  "message": "Expense deleted successfully"

}

6\.4 Clearing Expenses and Transactions

POST /api/transactions

Description: Record a payment transaction to settle an expense.

Request:

json

Copy code

{

  "fromUserId": "user-id-1",

  "toUserId": "user-id-2",

  "amount": 50.0,

  "method": "PayPal"

}

Response:

json

Copy code

{

  "success": true,

  "transactionId": "transaction-id"

}

GET /api/transactions/{transactionId}

Description: Get details of a specific transaction.

Response:

json

Copy code

{

  "transactionId": "transaction-id",

  "fromUserId": "user-id-1",

  "toUserId": "user-id-2",

  "amount": 50.0,

  "method": "PayPal",

  "date": "2023-01-01"

}

6\.5 Notifications

POST /api/notifications

Description: Send a notification.

Request:

json

Copy code

{

  "userId": "user-id",

  "message": "You have a new expense",

  "type": "email"

}

Response:

json

Copy code

{

  "success": true,

  "notificationId": "notification-id"

}

6\.6 Reports

GET /api/reports

Description: Generate an expense report.

Request:

json

Copy code

{

  "userId": "user-id",

  "groupId": "group-id",

  "startDate": "2023-01-01",

  "endDate": "2023-01-31"

}

Response:

json

Copy code

{

  "reportUrl": "https://example.com/reports/report-id"

}
