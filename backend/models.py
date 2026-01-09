from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
