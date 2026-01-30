from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "Wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.id"), unique=True)
    balance = Column(Float, default=0.0)

    user = relationship("User", back_populates="wallet")


class Cart(Base):
    __tablename__ = "Carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.id"), unique=True)

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "CartItems"
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("Carts.id"))
    product_id = Column(Integer, ForeignKey("Products.id"))
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Product(Base):
    __tablename__ = "Products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(225))
    price = Column(Float)
    image = Column(String(225))
    stock = Column(Integer)


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    firstName = Column(String(100))
    lastName = Column(String(100))
    username = Column(String(100), unique=True)
    password = Column(String(255))
    role = Column(String(100))

    wallet = relationship("Wallet", uselist=False, back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")
