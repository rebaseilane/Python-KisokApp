from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import User, Wallet, Cart
from backend.schemas import CreateUser, LoginUser, UserOut
from backend.core.auth import hash_password, verify_password, create_access_token
from backend.core.dependencies import get_current_user, admin_required

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
def register(user: CreateUser, db: Session = Depends(get_db)):
    """Create a new user with wallet and cart."""
    user.password = hash_password(user.password)
    new_user = User(**user.dict())
    
    # Create wallet
    new_user.wallet = Wallet(balance = 0.0)
    new_user.cart = Cart()
    # Create cart
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(
        {"sub": db_user.username, "role": db_user.role})
    return {
        "FirstName": db_user.firstName,
        "LastName": db_user.lastName,
        "token_type": "bearer",
        "access_token": token,
        }


@router.get("/get-users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "firstName": u.firstName,
            "lastName": u.lastName,
            "username": u.username,
            "role": u.role,
            "wallet_balance": u.wallet.balance if u.wallet else 0
        })
    return result



@router.get("/get-user-by-id/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@router.put("/update-user/{user_id}", response_model=UserOut)
def update_user(user_id: int, updated_user: CreateUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    for key, value in updated_user.dict().items():
        if key == "password":
            value = hash_password(value)
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
