# 📚 City Public Library API

This is a FastAPI backend project built as part of an internship program and demonstrates real-world API development using FastAPI.

---

## 🚀 Features

- REST APIs using FastAPI
- Pydantic data validation
- CRUD operations (Create, Read, Update, Delete)
- Search functionality
- Sorting results
- Combined browsing endpoint

---

## 📂 Project Structure

library_project/
│── main.py
│── requirements.txt
│── README.md
│── screenshots/

---

## 🛠 Tech Stack

- FastAPI
- Pydantic
- Uvicorn

---

## ▶️ How to Run

### 1. Install dependencies

pip install -r requirements.txt

### 2. Run FastAPI server

uvicorn main:app --reload

### 3. Open Swagger UI

http://127.0.0.1:8000/docs

---

## 📸 Screenshots

All API endpoints are tested using Swagger UI.

---

## 📌 API Functionalities

### ✅ GET APIs
- Home route
- Get all books
- Get book by ID
- Summary/count endpoint

### ✅ POST APIs
- Create new book
- Request body validation using Pydantic
- Field constraints and error handling

### ✅ Helper Functions
- find_book()
- filter_books()
- helper logic for search and validation

### ✅ CRUD Operations
- Create book
- Update book
- Delete book
- Proper status codes used:
  - 201 Created
  - 404 Not Found

### ✅ Multi-Step Workflow
- Borrow book
- Return book
- Queue system

### ✅ Advanced Features
- Search books
- Sort books
- Pagination
- Combined browse endpoint

---

## 🎯 Objective

This project demonstrates the ability to:
- Design RESTful APIs
- Structure backend systems
- Implement real-world workflows using FastAPI
- Follow FastAPI best practices and route structuring

---

## 🙌 Acknowledgment

Grateful for learning opportunity at Innomatics Research Labs.