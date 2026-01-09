from fastapi import FastAPI, Depends, Header, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.openapi.utils import get_openapi
from auth import create_access_token, decode_access_token
from db import SessionLocal
from models import Product, User
from schemas import ProductCreate, ProductOut, CreateUser, LoginUser
from auth import verify_password, hash_password


app = FastAPI(title="Kiosk Product API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dependency to get DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user


# Create Product
@app.post("/create-products", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    new = Product(**product.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# Get All Products


@app.get("/get-products", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Product).all()

# Update Product


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

# ----------------------------------------------------------------------------------------------------------------------------

# USER APIs


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Kiosk Product API",
        version="1.0",
        description="API with JWT Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.post("/user-register")
def register(user: CreateUser, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    new_user = User(
        firstName=user.firstName,
        lastName=user.lastName,
        username=user.username,
        password=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created!"}


@app.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"sub": db_user.username, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
