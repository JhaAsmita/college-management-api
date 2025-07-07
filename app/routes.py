from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import Student, User
from app.auth import authenticate_user, create_access_token, decode_token
from datetime import timedelta
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()

students_db = []

security = HTTPBearer()

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
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/students", dependencies=[Depends(get_current_user)])
def get_students():
    return students_db

@router.post("/students", dependencies=[Depends(get_current_user)])
def add_student(student: Student):
    students_db.append(student)
    return {"message": "Student added."}

@router.put("/students/{student_id}", dependencies=[Depends(get_current_user)])
def update_student(student_id: int, updated: Student):
    for i, s in enumerate(students_db):
        if s.id == student_id:
            students_db[i] = updated
            return {"message": "Student updated"}
    raise HTTPException(status_code=404, detail="Student not found")

@router.delete("/students/{student_id}", dependencies=[Depends(get_current_user)])
def delete_student(student_id: int):
    for i, s in enumerate(students_db):
        if s.id == student_id:
            students_db.pop(i)
            return {"message": "Student deleted"}
    raise HTTPException(status_code=404, detail="Student not found")
