from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import authenticate_user, create_access_token, decode_token
from app.models import Student
from app.database import SessionLocal
from pydantic import BaseModel
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    password: str

class StudentCreate(BaseModel):
    id: int
    name: str
    age: int
    department: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

@router.post("/login")
def login(user: User):
    if not authenticate_user(user.username, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.username}, access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/students")
def get_students(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(Student).all()

@router.post("/students")
def add_student(student: StudentCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    db.add(Student(**student.dict()))
    db.commit()
    return {"message": "Student added"}

@router.put("/students/{student_id}")
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in student.dict().items():
        setattr(db_student, field, value)
    db.commit()
    return {"message": "Student updated"}

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}
