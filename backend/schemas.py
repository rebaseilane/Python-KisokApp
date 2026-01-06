from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str
    stock: int


class ProductOut(ProductCreate):
    id: int

    class Config:
        form_attributes = True
