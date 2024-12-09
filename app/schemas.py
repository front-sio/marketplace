from pydantic import BaseModel, EmailStr, Field, root_validator
from datetime import datetime
from typing import Optional

# -------------------- User Schemas -------------------- #
class UserCreate(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr
    password: str
    role: str = Field(default="customer")  # Default role is "customer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  # Allows working with ORM objects

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True



# -------------------- Business Owner Schemas -------------------- #


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


# -------------------- Business Owner Schemas -------------------- #
class BusinessOwnerCreate(BaseModel):
    business_name: str = Field(..., max_length=255)
    description: Optional[str]
    email: Optional[EmailStr]
    password: str
    phone: Optional[str]  # Make sure this is Optional
    address: Optional[str]
    

class BusinessOwnerResponse(BaseModel):
    id: int
    business_name: str
    description: Optional[str] = None  # Make description optional
    phone: Optional[str] = None
    address: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True



    @root_validator(pre=True)
    def check_description(cls, values):
        # You can check or modify 'description' here
        if 'description' in values and values['description'] == "":
            values['description'] = None  # Properly set it to None if it's an empty string
        return values




class CategoryCreateSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True

class CategorySchema(CategoryCreateSchema):
    id: int

    class Config:
        from_attributes = True



# -------------------- Product Schemas -------------------- #
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    category_id: int  # The ID of the Category
    price: float
    quantity: int
    description: Optional[str]
    seller_id: int  # The ID of the BusinessOwner selling the product
    image: str

class ProductResponse(BaseModel):
    id: int
    name: str
    category: int  # Use category name instead of ID
    price: float
    quantity: int
    description: Optional[str]
    seller_id: int
    image: Optional[str]  # Include image URL in response

    class Config:
        from_attributes = True



class ProductWithImageUrl(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None
    image_url: str  # Add image_url field

    class Config:
        from_attributes = True



# -------------------- Order Schemas -------------------- #
# Assuming you have an ORM model `Order` and `Product` for price
class OrderCreate(BaseModel):
    product_id: int
    buyer_id: int
    quantity: int
    status: str = Field(default="Pending", max_length=50)




class OrderResponse(BaseModel):
    id: int
    product_id: int
    buyer_id: int
    quantity: int
    status: str

    class Config:
        from_attributes = True

    

    # This function is a placeholder to get the price of the product
    def fetch_product_price(self, product_id: int) -> float:
        # Fetch the product price from the database or from the ORM model
        product = Product.get(id=product_id)  # Example using ORM (e.g., Tortoise)
        return product.price  # Assuming 'price' is a field in the Product model




# -------------------- Shipping Company Schemas -------------------- #
class ShippingCompanyCreate(BaseModel):
    name: str = Field(..., max_length=255)
    email: Optional[EmailStr]
    password: str
    contact: Optional[str]
    address: Optional[str]

class ShippingCompanyResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    address: Optional[str]
    user_id: int

    class Config:
        from_attributes = True






# -------------------- Shipping Schemas -------------------- #
class ShippingCreate(BaseModel):
    order_id: int
    shipping_company_id: int
    tracking_number: str = Field(..., max_length=255)  # Required field
    status: str = Field(default="Pending", max_length=50)  # Optional field with a default value
    cost: float

class ShippingResponse(BaseModel):
    id: int
    order_id: int
    shipping_company_id: int
    tracking_number: str
    status: str
    cost: float

    class Config:
        from_attributes = True






# -------------------- Tutorial Schemas -------------------- #

class TutorialBase(BaseModel):
    title: str
    description: str
    content: str

class TutorialCreate(TutorialBase):
    pass

class TutorialResponse(TutorialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True