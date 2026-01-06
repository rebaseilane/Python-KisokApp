from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Product
from schemas import ProductCreate, ProductOut

app = FastAPI(title="Kiosk Product API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Product
@app.post("/create-products", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new = Product(**product.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


# Get All Products
@app.get("/get-products", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# Update Product


@app.put("/update-products/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    item = db.query(Product).filter(Product.id == product_id).first()
    item.name = product.name
    item.description = product.description
    item.price = product.price
    item.image = product.image
    item.stock = product.stock
    db.commit()
    return {"message": "Updates"}


# Delete products
@app.delete("/delete-products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    item = db.query(Product).filter(Product.id == product_id).first()
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
