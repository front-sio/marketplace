from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime




# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User Model
class User(Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=255)
    role = fields.CharField(max_length=50, default="customer")  # Roles: "customer", "business_owner", etc.

    # Optional Reverse Relation (only needed if explicitly accessed)
    business_owner_profile = fields.OneToOneField(
        "models.BusinessOwner",
        related_name="business_profile",
        null=True,
        on_delete=fields.CASCADE,
    )  # This creates a one-to-one relationship

    shipping_company_profile = fields.OneToOneField(
        "models.ShippingCompany",
        related_name="shipping_company_profile",
        null=True,
        on_delete=fields.CASCADE,
    )  # This creates a one-to-one relationship

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password using bcrypt."""
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify if the plain password matches the hashed password."""
        return pwd_context.verify(plain_password, hashed_password)


# Business Owner Model
class BusinessOwner(Model):
    id = fields.IntField(pk=True)
    business_name = fields.CharField(max_length=255)
    address = fields.TextField()
    phone = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    # No need for 'user' field in BusinessOwner, because 'User' already links to it
    # Just have the foreign key relationship in the User model.
    user_id = fields.IntField()

    def __str__(self):
        return self.business_name





# Category Model
class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    
    # Reverse relationship to products
    products = fields.ReverseRelation["Product"]
    
    def __str__(self):
        return self.name





# Product Model
class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    category = fields.ForeignKeyField("models.Category", related_name="products", null=False)  # ForeignKey to Category
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField(default=0)  # Default to 0 if no quantity is provided
    description = fields.TextField(null=True)  # Allow null values for description
    image = fields.CharField(max_length=255, null=True)  # Field for image URL (could be a path or URL)

    # Seller relationship
    seller = fields.ForeignKeyField("models.BusinessOwner", related_name="products", null=True)  # Seller can be optional

    # Reverse relationship for orders
    orders = fields.ReverseRelation["Order"]

    def __str__(self):
        return self.name
    


class Offer(Model):
    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField("models.Product", related_name="offers")  # The product this offer is related to
    price_from = fields.DecimalField(max_digits=10, decimal_places=2)  # Original price
    discount_price = fields.DecimalField(max_digits=10, decimal_places=2)  # Price after discount
    quantity_set = fields.IntField()  # Quantity available for the offer
    min_order = fields.IntField()  # Minimum quantity for an order
    max_order = fields.IntField()  # Maximum quantity for an order
    start_date = fields.DatetimeField(default=datetime.utcnow)  # Offer start date
    end_date = fields.DatetimeField()  # Offer end date
    created_at = fields.DatetimeField(auto_now_add=True)  # Created date for the offer
    updated_at = fields.DatetimeField(auto_now=True)  # Last updated date for the offer

    def __str__(self):
        return f"Offer on {self.product.name} with {self.discount_price} discounted price"

    class Meta:
        table = "offers"



# Order Model
class Order(Model):
    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField("models.Product", related_name="orders")
    buyer = fields.ForeignKeyField("models.User", related_name="orders")
    quantity = fields.IntField()
    status = fields.CharField(
        max_length=50, 
        choices=["Pending", "Completed", "Shipped"],
        default="Pending"
    )

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    @property
    def total_price(self):
        product = self.product  # Fetch product object using the ForeignKey relationship
        return self.quantity * product.price  # Assuming 'price' is a field in the Product model


# Shipping Company Model
class ShippingCompany(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    contact = fields.CharField(max_length=50)
    address = fields.TextField()
    user_id = fields.IntField(null=True)  # Adjusted to avoid direct cyclic FK

    def __str__(self):
        return self.name


# Shipping Model
class Shipping(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order", related_name="shipping")
    shipping_company = fields.ForeignKeyField("models.ShippingCompany", related_name="shippings")
    tracking_number = fields.CharField(max_length=255)
    status = fields.CharField(
        max_length=50,
        choices=["Pending", "In Transit", "Delivered"],
        default="Pending"
    )
    cost = fields.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Shipping {self.id} - {self.status}"





class Tutorial(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tutorials"

    def __str__(self):
        return self.title






User_Pydantic = pydantic_model_creator(User, name="User")
User_PydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
User_PydanticOut = pydantic_model_creator(User, name="UserOut", exclude=("password", ))

Product_Pydantic = pydantic_model_creator(Product, name="Product")
Product_PydanticIn = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)
Order_Pydantic = pydantic_model_creator(Order, name="Order")
Order_PydanticIn = pydantic_model_creator(Order, name="OrderIn", exclude_readonly=True)
Shipping_Pydantic = pydantic_model_creator(Shipping, name="Shipping")
Shipping_PydanticIn = pydantic_model_creator(Shipping, name="ShippingIn", exclude_readonly=True)
ShippingCompany_Pydantic = pydantic_model_creator(ShippingCompany, name="ShippingCompany")
ShippingCompany_PydanticIn = pydantic_model_creator(ShippingCompany, name="ShippingCompanyIn", exclude_readonly=True)
Tutorial_Pydantic = pydantic_model_creator(Tutorial, name="Tutorial")
Tutorial_PydanticIn = pydantic_model_creator(Tutorial, name="TutorialIn", exclude_readonly=True)





# Add computed `image_url` property
class ProductWithImageUrl(Product_Pydantic):
    @property
    def image_url(self) -> Optional[str]:
        if self.image:
            return f"/static/images/{self.image}"  # Assuming image is stored in a static folder
        return None  # Return None or placeholder if no image available
        