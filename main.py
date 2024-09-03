from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb+srv://parth01:parth123@cluster0.77are8z.mongodb.net/?retryWrites=true&w=majority")
db = client["Library"]
collection = db["students"]

app = FastAPI(
    title="Student Library",
    docs_url="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

@app.post("/students/", status_code=201, tags=["Students"])
def create_student(student: Student):
    student_dict = student.dict()
    result = collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

@app.get("/students/", response_model=dict, tags=["Students"])
def list_students(country: str = None, age: int = None):
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    
    students = list(collection.find(query))
    # Convert _id to string but also keep the original _id field
    for student in students:
        student["_id"] = str(student["_id"])
    
    return {"data": students}

@app.get("/students/{student_id}", response_model=dict, tags=["Students"])
def get_student(student_id: str):
    student = collection.find_one({"_id": ObjectId(student_id)})
    if student:
        student["_id"] = str(student["_id"])
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{student_id}", status_code=204, tags=["Students"])
def update_student(student_id: str, student: Student):
    student_dict = student.dict(exclude_unset=True)
    result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}", tags=["Students"])
def delete_student(student_id: str):
    result = collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student_id}
