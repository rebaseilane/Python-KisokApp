from pydantic import BaseModel, Field, validator
import re


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str
    stock: int


class CreateUser(BaseModel):
    firstName: str = Field(min_length=2)
    lastName: str = Field(min_length=2)
    username: str = Field(min_length=2)
    password: str
    role: str

    @validator("password")
    def strong_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not re.search(r"\d", v):
            raise ValueError("Password must include a number")
        if not re.search(r"[!@#$%^&*()_+=\-]", v):
            raise ValueError("Password must include a special character")
        return v


class LoginUser(BaseModel):
    username: str
    password: str


class ProductOut(ProductCreate):
    id: int

    class Config:
        from_attributes = True
