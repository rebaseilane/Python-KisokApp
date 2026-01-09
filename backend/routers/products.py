from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Product
from schemas import ProductCreate, ProductOut
from dependencies import admin_required, get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/create-products", response_model=ProductOut)
def create(product:ProductCreate, db:Session=Depends(get_db), user=Depends(admin_required)):
    p = Product(**product.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.get("/all-products", response_model=list[ProductOut])
def all(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(Product).all()

@app.put("/update-products/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Product).filter(Product.id == product_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    item.name = product.name
    item.description = product.description
    item.price = product.price
    item.image = product.image
    item.stock = product.stock
    db.commit()
    return {"message": "Product updated"}


# Delete products
@app.delete("/delete-products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    item = db.query(Product).filter(Product.id == product_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(item)
    db.commit()
    return {"message": "Product deleted"}

