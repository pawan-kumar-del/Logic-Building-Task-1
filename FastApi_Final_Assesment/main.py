#Intern ID : IN126014402

from fastapi import Query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="📚 City Public Library API", description="Final Internship Project", version="1.0")

# ==================================================
# Q1 — HOME
# ==================================================
@app.get("/", summary="Q1: Home Endpoint")
def home():
    return {"message": "Welcome to City Public Library"}

# ==================================================
# DATA
# ==================================================
books = [
    {"id": 1, "title": "Python Basics", "author": "John", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "AI World", "author": "Andrew", "genre": "Science", "is_available": True},
    {"id": 3, "title": "History India", "author": "Sharma", "genre": "History", "is_available": True},
    {"id": 4, "title": "Fiction Life", "author": "Jane", "genre": "Fiction", "is_available": True},
    {"id": 5, "title": "Deep Learning", "author": "Ng", "genre": "Tech", "is_available": True},
    {"id": 6, "title": "World War", "author": "Max", "genre": "History", "is_available": True},
]

borrow_records = []
queue = []
record_counter = 1

# ==================================================
# HELPERS
# ==================================================
def find_book(book_id):
    return next((b for b in books if b["id"] == book_id), None)

def is_book_borrowed(book_id):
    return any(r["book_id"] == book_id and not r.get("returned", False) for r in borrow_records)

def calculate_due_date(days, member_type="regular"):
    if member_type == "premium":
        days = min(days, 60)
    else:
        days = min(days, 30)
    return f"Return by Day {15 + days}"

def filter_books_logic(genre, author, is_available):
    result = books
    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]
    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]
    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]
    return result

# ==================================================
# Q2 — GET BOOKS
# ==================================================
@app.get("/books", summary="Q2: Get All Books with Count")
def get_books():
    available = len([b for b in books if b["is_available"]])
    return {"total": len(books), "available_count": available, "books": books}

# ==================================================
# Q5 — SUMMARY
# ==================================================
@app.get("/books/summary", summary="Q5: Books Summary")
def summary():
    genre_count = {}
    for b in books:
        genre_count[b["genre"]] = genre_count.get(b["genre"], 0) + 1

    available = len([b for b in books if b["is_available"]])

    return {
        "total": len(books),
        "available": available,
        "borrowed": len(books) - available,
        "genres": genre_count
    }

# ==================================================
# Q4 — BORROW RECORDS
# ==================================================
@app.get("/borrow-records", summary="Q4: Get Borrow Records")
def get_records():
    return {"total": len(borrow_records), "records": borrow_records}

# ==================================================
# Q6 — MODEL
# ==================================================
class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=60)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

# ==================================================
# Q8 — BORROW
# ==================================================
@app.post("/borrow", summary="Q8: Borrow Book")
def borrow(req: BorrowRequest):
    global record_counter

    if req.member_type.lower() == "regular" and req.borrow_days > 30:
        raise HTTPException(400, "Regular members max 30 days")

    book = find_book(req.book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    if not book["is_available"]:
        raise HTTPException(400, "Already borrowed")

    book["is_available"] = False
    
    record = {
        "record_id": record_counter,
        "member_name": req.member_name,
        "member_id": req.member_id,
        "book_id": req.book_id,
        "due_date": calculate_due_date(req.borrow_days, req.member_type),
        "returned": False   
    }


    borrow_records.append(record)
    record_counter += 1

    return {"message": "Book borrowed", "record": record}

# ==================================================
# Q10 — FILTER
# ==================================================
@app.get("/books/filter", summary="Q10: Filter Books")
def filter_books(
    genre: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None)
):
    result = filter_books_logic(genre, author, is_available)
    return {"count": len(result), "books": result}

# ==================================================
# Q11 — ADD BOOK
# ==================================================
class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

@app.post("/books", summary="Q11: Add New Book", status_code=201)
def add_book(book: NewBook):
    if any(b["title"].lower() == book.title.lower() for b in books):
        raise HTTPException(400, "Duplicate title")

    new = book.dict()
    new["id"] = max([b["id"] for b in books], default=0) + 1
    books.append(new)

    return {"message": "Book added", "book": new}

# ==================================================
# Q12 — UPDATE
# ==================================================
@app.put("/books/{book_id}", summary="Q12: Update Book")
def update_book(book_id: int, genre: Optional[str] = None, is_available: Optional[bool] = None):
    book = find_book(book_id)
    if not book:
        raise HTTPException(404, "Not found")

    if genre is not None:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available

    return {"message": "Updated", "book": book}

# ==================================================
# Q13 — DELETE
# ==================================================
@app.delete("/books/{book_id}", summary="Q13: Delete Book", status_code=200)
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(404, "Not found")

    if is_book_borrowed(book_id):
        raise HTTPException(400, "Cannot delete borrowed book")

    books.remove(book)
    return {"message": "Book deleted successfully"}

# ==================================================
# Q14 — QUEUE
# ==================================================
@app.post("/queue/add", summary="Q14: Add to Queue")
def add_queue(member_name: str, book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(404, "Not found")

    if book["is_available"]:
        raise HTTPException(400, "Book available")

    if any(q["member_name"] == member_name and q["book_id"] == book_id for q in queue):
        raise HTTPException(400, "Already in queue")
    
    queue.append({"member_name": member_name, "book_id": book_id})
    return {"message": "Added to queue"}

@app.get("/queue", summary="Q14: View Queue")
def get_queue():
    return {"total": len(queue), "queue": queue}

# ==================================================
# Q15 — RETURN
# ==================================================
@app.post("/return/{book_id}", summary="Q15: Return Book Workflow")
def return_book(book_id: int):
    global record_counter

    book = find_book(book_id)

    if not book:
        raise HTTPException(404, "Not found")
    
    if not is_book_borrowed(book_id):
        raise HTTPException(400, "Book was not borrowed")
    
    for r in borrow_records:
        if r["book_id"] == book_id and not r.get("returned", False):
            r["returned"] = True
            break

    book["is_available"] = True

    for q in queue.copy():
        if q["book_id"] == book_id:
            queue.remove(q)
            book["is_available"] = False
            
            record = {
                "record_id": record_counter,
                "member_name": q["member_name"],
                "member_id": "queue_user",
                "book_id": book_id,
                "due_date": "Auto-assigned",
                "returned": False
            }

            borrow_records.append(record)
            record_counter += 1
            return {"message": "Returned and reassigned", "record": record}

    return {"message": "Returned and available"}

# ==================================================
# Q16 — SEARCH
# ==================================================
@app.get("/books/search", summary="Q16: Search Books")
def search(keyword: str = Query(..., min_length=1)):
    result = [b for b in books if keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()]
    if not result: 
        return {"message": "No books found"}
    
    return {"total_found": len(result), "results": result}

# ==================================================
# Q17 — SORT
# ==================================================
@app.get("/books/sort", summary="Q17: Sort Books")
def sort_books(sort_by: str = "title", order: str = "asc"):
    if sort_by not in ["title", "author", "genre"]:
        raise HTTPException(400, "Invalid sort")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    return {"books": sorted(books, key=lambda x: x[sort_by], reverse=(order=="desc"))}

# ==================================================
# Q18 — PAGINATION
# ==================================================
@app.get("/books/page", summary="Q18: Pagination")
def paginate(page: int = Query(1, gt=0), limit: int = Query(3, gt=0, le=10)):
    start = (page-1)*limit
    end = start+limit
    total_pages = (len(books)+limit-1)//limit

    return {"page": page, "total_pages": total_pages, "data": books[start:end]}

# ==================================================
# Q19 — BORROW SEARCH + PAGE
# ==================================================
@app.get("/borrow-records/search", summary="Q19: Search Borrow Records")
def search_records(name: str = Query(..., min_length=1)):
    result = [r for r in borrow_records if name.lower() in r["member_name"].lower()]
    return {
         "total_found": len(result),
        "records": result
    }
@app.get("/borrow-records/page", summary="Q19: Paginate Borrow Records")
def page_records(page: int = Query(1, gt=0), limit: int = Query(2, gt=0, le=10)):
    start = (page-1)*limit
    end = start+limit
    total = len(borrow_records)
    total_pages = (total + limit - 1) // limit
    
    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "records": borrow_records[start:end]
}

# ==================================================
# Q20 — BROWSE
# ==================================================
@app.get("/books/browse", summary="Q20: Combined Browse (Search + Sort + Pagination)")
def browse(keyword: Optional[str] = None, sort_by: str = "title", order: str = "asc", page: int = 1, limit: int = 3):

    if sort_by not in ["title", "author", "genre"]:
        raise HTTPException(400, "Invalid sort")

    if order not in ["asc", "desc"]: 
        raise HTTPException(400, "Invalid order")

    result = books

    if keyword:
        result = [b for b in result if keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()]

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order=="desc"))

    start = (page-1)*limit
    end = start+limit

    return {
        "total": len(result),
        "page": page,
        "limit": limit,
        "results": result[start:end]
    }

# ==================================================
# Q3 — GET BOOK BY ID
# ==================================================
@app.get("/books/{book_id}", summary="Q3: Get Book by ID")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book