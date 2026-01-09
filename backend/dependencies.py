from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth import decode_access_token
from db import SessionLocal
from models import User

# Now these dependencies can be used in route definitions to enforce authentication and authorization.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username==payload.get("sub")).first()
    if not user:
        raise HTTPException(401,"Invalid token")
    return user

def admin_required(user=Depends(get_current_user)):
    if user.role!="admin":
        raise HTTPException(403,"Admins only")
    return user
