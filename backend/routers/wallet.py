from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import Wallet, User
from backend.core.dependencies import get_current_user, admin_required

router = APIRouter(prefix="/wallet", tags=["Wallet"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# View user wallet
@router.get("/my-wallet")
def get_my_wallet(db: Session = Depends(get_db), user = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    return {
        "user_id": wallet.user_id,
        "balance": wallet.balance
    }


#View All user's wallets (Admin only)
@router.get("/all-wallets")
def get_all_wallets(admin: User = Depends(admin_required), db: Session = Depends(get_db)):
    wallets = db.query(Wallet).all()
    return [
        {
            "wallet_id": w.id,
            "user_id": w.user_id,
            "username": w.user.username,
            "balance": w.balance
        }
        for w in wallets
    ]



@router.get("/wallets/{user_id}")
def get_user_wallet(user_id: int, admin: User = Depends(admin_required), db: Session = Depends(get_db)):
    """Admins can view a specific user's wallet"""
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {
        "wallet_id": wallet.id,
        "user_id": wallet.user_id,
        "username": wallet.user.username,
        "balance": wallet.balance
    }




# Fund user wallet
@router.post("/fund")
def fund_wallet(amount: float, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be more than 0")
    
    if amount > 1500:
        raise HTTPException(status_code=400, detail="Amount cannot exceed R1 500")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    
    wallet.balance = wallet.balance + amount
    db.commit()

    return {
        "message": "Wallet funded successfully",
        "balance": wallet.balance
    }
