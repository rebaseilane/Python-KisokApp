from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import Cart, CartItem, Product, User
from backend.core.dependencies import get_current_user, admin_required

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# View user's cart


@router.get("/my-cart")
def get_my_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if cart is None or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    items = []
    total_price = 0
    for item in cart.items:
        item_total = item.quantity * item.product.price
        total_price += item_total
        items.append({
            "product_id": item.product_id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return {
        "cart_id": cart.id,
        "user_id": cart.user_id,
        "total_items": len(cart.items),
        "total_price": total_price,
        "items": items
    }


# Add products in the cart
@router.post("/add")
def add_to_cart(product_id: int, quantity: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=400, detail="Product not found")

    if quantity <= 0:
        raise HTTPException(
            status_code=400, detail="Quantity must be more than 0")

    if product.stock < quantity:
        raise HTTPException(
            status_code=400, detail=f"Only {product.stock} items available in stock")

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id,
                                     CartItem.product_id == product_id).first()

    if item:
        if product.stock < item.quantity + quantity:
            raise HTTPException(
                status_code=400, detail=f"Only {product.stock - item.quantity} more items can be added")
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id,
                        quantity=quantity)
        db.add(item)

    product.stock -= quantity

    db.commit()
    return {"message": "Product successfully added to cart"}


# Update product quantity in cart
@router.put("/update")
def update_cart_item(product_id: int, quantity: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if quantity < 0:
        raise HTTPException(
            status_code=400, detail="Quantity cannot be negative")

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if cart is None:
        raise HTTPException(status_code=400, detail="Cart not found")

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id,
                                     CartItem.product_id == product_id).first()
    product = db.query(Product).filter(Product.id == product_id).first()

    if item is None:
        raise HTTPException(status_code=400, detail="Item not found in cart")

    # If user wants to increase quantity
    if quantity > item.quantity:
        diff = quantity - item.quantity
        if product.stock < diff:
            raise HTTPException(
                status_code=400, detail=f"Only {product.stock} items available in stock")
        product.stock -= diff
    # If user wants to decrease quantity
    elif quantity < item.quantity:
        diff = item.quantity - quantity
        product.stock += diff

    item.quantity = quantity

    # If quantity becomes 0, remove the item
    if item.quantity == 0:
        db.delete(item)

    db.commit()
    return {"message": "Cart updated successfully", "cart_item_quantity": quantity, "remaining_stock": product.stock}


# Remove products in the cart
@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id,
                                     CartItem.product_id == product_id).first()

    if item is None:
        raise HTTPException(status_code=400, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item removed"}


@router.get("/carts")
def get_all_carts(admin: User = Depends(admin_required), db: Session = Depends(get_db)):
    """Admins can view all carts"""
    carts = db.query(Cart).all()
    result = []
    for cart in carts:
        items = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "item_total": item.quantity * item.product.price
            }
            for item in cart.items
        ]
        result.append({
            "cart_id": cart.id,
            "user_id": cart.user_id,
            "username": cart.user.username,
            "total_items": len(items),
            "total_price": sum(i["item_total"] for i in items),
            "items": items
        })
    return result


@router.get("/carts/{user_id}")
def get_user_cart(user_id: int, admin: User = Depends(admin_required), db: Session = Depends(get_db)):
    """Admins can view a specific user's cart"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price,
            "item_total": item.quantity * item.product.price
        }
        for item in cart.items
    ]
    
    return {
        "cart_id": cart.id,
        "user_id": cart.user_id,
        "username": cart.user.username,
        "total_items": len(items),
        "total_price": sum(i["item_total"] for i in items),
        "items": items
    }
