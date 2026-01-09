from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User
from schemas import CreateUser, LoginUser
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/register")
def register(user:CreateUser, db:Session=Depends(get_db)):
    user.password = hash_password(user.password)
    db.add(User(**user.dict()))
    db.commit()
    return {"message":"Account created"}

@router.post("/login")
def login(user:LoginUser, db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username==user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401,"Invalid credentials")
    token = create_access_token({"sub":db_user.username,"role":db_user.role})
    return {"access_token":token}


@router.get("/get-users", response_model=list[User], dependencies=[Depends(get_db)])
def get_users(db:Session=Depends(get_db)):
    return db.query(User).all()
