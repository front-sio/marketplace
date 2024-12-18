from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import init_db
from tortoise.contrib.pydantic import pydantic_model_creator
from app.core.security import get_current_user  # Assuming you have a function to get the logged-in user
from typing import Optional
from app.services.category_service import create_category, get_category_by_id, get_all_categories
from typing import List
from fastapi.responses import JSONResponse
from io import BytesIO
from pathlib import Path
import shutil




from app.models import (
    Offer,
    User_Pydantic,
    User_PydanticIn,
    Product_Pydantic,
    Product_PydanticIn,
    Order_Pydantic,
    Order_PydanticIn,
    Shipping_Pydantic,
    Shipping_PydanticIn,
    ShippingCompany_Pydantic,
    ShippingCompany_PydanticIn,
    Tutorial_Pydantic,
    Tutorial_PydanticIn,
)
from app.models import (
    User, 
    Product, 
    Order, 
    Shipping, 
    ShippingCompany, 
    Tutorial,
    BusinessOwner,
    Category
)
from app.schemas import (
    ProductWithImageUrl,
    UserCreate, 
    LoginRequest, 
    UserResponse, 
    SignInResponse,
    ProductCreate, 
    ProductResponse, 
    OfferRequest,
    OfferResponse,
    OrderCreate, 
    OrderResponse, 
    ShippingCreate, 
    ShippingResponse, 
    ShippingCompanyCreate, 
    ShippingCompanyResponse, 
    TutorialCreate, 
    TutorialResponse,
    BusinessOwnerResponse,
    BusinessOwnerCreate,
    CategoryCreateSchema, CategorySchema,
    CategoryResponse,
    SummaryResponse
)



import logging

logger = logging.getLogger(__name__)


# router api
router = APIRouter()


# User Endpoints
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    await init_db()
    
    try:
        db_user = await User.get(email=user.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    except DoesNotExist:
        pass

    hashed_password = hash_password(user.password)
    new_user = await User.create(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    return new_user



@router.post("/register/business_owner", response_model=BusinessOwnerResponse)
async def register_business_owner(business_owner_data: BusinessOwnerCreate):
    # Check if the email already exists in the system
    existing_user = await User.get_or_none(email=business_owner_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    # Hash the password provided by the user
    hashed_password = hash_password(business_owner_data.password)

    # Create a new user with the role "business_owner"
    user = User(
        first_name=business_owner_data.first_name,
        last_name=business_owner_data.last_name,
        username=business_owner_data.username,
        email=business_owner_data.email,
        hashed_password=hashed_password,
        role="business_owner",
    )
    # Save the user first
    await user.save()

    # Save the business owner information with the user_id correctly set
    business_owner = BusinessOwner(
        business_name=business_owner_data.business_name,
        phone=business_owner_data.phone,
        address=business_owner_data.address,
        user_id=user.id,  # Explicitly set the user_id
    )
    await business_owner.save()

    # Return the response
    return BusinessOwnerResponse(
        id=business_owner.id,
        business_name=business_owner.business_name,
        phone=business_owner.phone,
        address=business_owner.address,
        user_id=user.id,
    )





@router.post("/token")
async def login_for_access_token(login_data: LoginRequest):
    try:
        user = await User.get(email=login_data.email)
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        },
    }





@router.post("/categories", response_model=CategoryResponse)
async def add_category(category: CategoryCreateSchema):
    # Create category logic (e.g., database operation)
    category_instance = await create_category(category.name)  # Assuming `create_category` is implemented
    return category_instance


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def fetch_category(category_id: int):
    category = await get_category_by_id(category_id)
    return category

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories():
    categories = await get_all_categories()
    return categories





@router.post("/products", response_model=ProductResponse)
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: Optional[str] = Form(None),
    seller_id: int = Form(...),
    image: UploadFile = File(...),
):
    # Step 1: Check if the user exists based on seller_id
    try:
        user = await User.get(id=seller_id)  # Fetch the user by seller_id
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="User does not exist")

    # Step 2: Get the BusinessOwner related to the user
    try:
        business_owner = await BusinessOwner.get(user_id=user.id)  # Fetch the business owner by user_id
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Business owner does not exist for this user")

    # Step 3: Now we have the business owner, use its ID to set the seller_id
    seller_id = business_owner.id

    # Step 4: Handle image upload if provided
    image_url = None
    if image:
        image_path = Path("static/images") / image.filename
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_url = str(image_path)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    # Step 5: Get or create the category object
    try:
        category = await Category.get(id=category_id)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Category does not exist")

    # Step 6: Create the product
    db_product = await Product.create(
        name=name,
        category=category,
        price=price,
        quantity=quantity,
        description=description,
        seller_id=seller_id,  # Use seller_id from BusinessOwner
        image=image_url if image else None
    )

    # Step 7: Return the created product response
    return ProductResponse(
        id=db_product.id,
        name=db_product.name,
        price=db_product.price,
        quantity=db_product.quantity,
        description=db_product.description,
        seller_id=db_product.seller_id,
        category_id=db_product.category.id,  # Access the category's ID
        image=db_product.image
    )



@router.get("/products", response_model=list[ProductWithImageUrl])
async def get_products(request: Request, skip: int = 0, limit: int = 100):
    """
    Get a list of products with pagination.
    """
    products = await Product_Pydantic.from_queryset(Product.all().offset(skip).limit(limit))

    if not products:
        return []  # Return an empty list if no products are found

    products_with_url = []
    for product in products:
        product_dict = product.dict()  # Convert to dictionary
        if product.image:
            product_dict['image_url'] = f"{request.base_url}{product.image}"
        else:
            product_dict['image_url'] = 'https://placehold.co/400'  # Fallback image URL

        products_with_url.append(product_dict)

    return products_with_url





@router.post("/offers", response_model=OfferResponse)
async def create_offer(offer: OfferRequest):
    # Get the product from the database using the product_id
    try:
        product = await Product.get(id=offer.product_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if the quantity available in the offer does not exceed the product's available stock
    if offer.quantity_set > product.quantity:
        raise HTTPException(status_code=400, detail="Offer quantity cannot exceed product's available stock")

    # Create the offer in the database
    new_offer = await Offer.create(
        product=product,
        price_from=offer.price_from,
        discount_price=offer.discount_price,
        quantity_set=offer.quantity_set,
        min_order=offer.min_order,
        max_order=offer.max_order,
        end_date=offer.end_date
    )

    # Reduce the product quantity by the offer quantity
    product.quantity -= offer.quantity_set
    await product.save()

    # Return the created offer
    return OfferResponse.from_attributes(new_offer)



# Order Endpoints

@router.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    try:
        order_obj = await Order.create(**order.dict())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    return OrderResponse.from_orm(order_obj)


@router.get("/orders", response_model=list[Order_Pydantic])
async def get_orders(skip: int = 0, limit: int = 100):
    """
    Get a list of products with pagination.
    - skip: The number of records to skip (default is 0).
    - limit: The maximum number of records to return (default is 100).
    """
    orders = await Order_Pydantic.from_queryset(Order.all().offset(skip).limit(limit))
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    
    return orders



# Shipping Endpoints
@router.post("/shipping", response_model=ShippingResponse)
async def create_shipping(shipping: ShippingCreate):
    try:
        shipping_obj = await shipping.create(**shipping.dict())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    return ShippingResponse.from_attributes(shipping_obj)





@router.get("/shipping", response_model=list[Shipping_Pydantic])
async def get_shipping(skip: int = 0, limit: int = 100):
    """
    Get a list of products with pagination.
    - skip: The number of records to skip (default is 0).
    - limit: The maximum number of records to return (default is 100).
    """
    shipping = await Shipping_Pydantic.from_queryset(Shipping.all().offset(skip).limit(limit))
    
    if not shipping:
        raise HTTPException(status_code=404, detail="No shipping found")
    
    return shipping





"""
here we allow shipping and delivery companies to register
"""
# ShippingCompany Endpoints
@router.post("/register-shipping-company", response_model=ShippingCompanyResponse)
async def create_shipping_company(shipping_company_data: ShippingCompanyCreate):

  
    # Check if the email already exists in the system
    existing_user = await User.get_or_none(email=shipping_company_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Hash the password provided by the user
    hashed_password = pwd_context.hash(shipping_company_data.password)

    # Create a new user with the role "business_owner"
    user = User(
        name=shipping_company_data.name,  # Use business_name as user name for simplicity
        email=shipping_company_data.email,  # Use email as user identifier
        hashed_password=hashed_password,  # Store the hashed password
        role="business_owner"
    )

    # Save the user
    await user.save()


    """
    Create the business owner profile,
    this allow user to register as business owner, in 
    """
    shipping_company_profile = ShippingCompany(
        name=shipping_company_data.name,
        email=shipping_company_data.email,
        contact=shipping_company_data.contact,
        address=shipping_company_data.address,
        user_id=user.id  # Associate the user with the business owner profile
    )


    await shipping_company_profile.save()

    return ShippingCompanyResponse.from_orm(shipping_company_profile)


# get all shipping companies
@router.get("/shipping-company", response_model=list[ShippingCompany_Pydantic])
async def get_shipping_companies(skip: int = 0, limit: int = 100):
    """
    Get a list of products with pagination.
    - skip: The number of records to skip (default is 0).
    - limit: The maximum number of records to return (default is 100).
    """
    shipping_companies = await ShippingCompany_Pydantic.from_queryset(ShippingCompany.all().offset(skip).limit(limit))
    
    if not shipping_companies:
        raise HTTPException(status_code=404, detail="No shipping company found")
    
    return shipping_companies




# Tutorial Endpoints (Learning Center)
@router.post("/tutorials", response_model=Tutorial_Pydantic)
async def create_tutorial(tutorial: Tutorial_PydanticIn):
    tutorial_obj = await Tutorial.create(**tutorial.dict())
    return await Tutorial_Pydantic.from_tortoise_orm(tutorial_obj)

@router.get("/tutorials", response_model=list[Tutorial_Pydantic])
async def get_tutorials():
    return await Tutorial_Pydantic.from_queryset(Tutorial.all())









# Endpoint to get the summary of various metrics
@router.get("/summary", response_model=SummaryResponse)
async def get_summary(current_user: str = Depends(get_current_user)):
    try:
        # Total number of products
        total_products = await Product.all().count()

        # Total number of orders
        total_orders = await Order.all().count()

        # Total value of products (sum of price * quantity)
        total_product_value = await Product.all().annotate(
            total_value=(Product.price * Product.quantity)
        ).all()

        total_product_value = sum(product.total_value for product in total_product_value)

        # Total value of orders (sum of price * quantity)
        total_order_value = await Order.all().annotate(
            total_value=(Order.price * Order.quantity)
        ).all()

        total_order_value = sum(order.total_value for order in total_order_value)

        # Restrict access to shipping companies and business owners for normal users
        if current_user.role == "business_owner":
            total_shipping_companies = await ShippingCompany.all().count()
            total_business_owners = await BusinessOwner.all().count()
        else:
            total_shipping_companies = 0
            total_business_owners = 0

        return SummaryResponse(
            total_products=total_products,
            total_orders=total_orders,
            total_shipping_companies=total_shipping_companies,
            total_business_owners=total_business_owners,
            total_product_value=total_product_value,
            total_order_value=total_order_value
        )

    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail=f"Resource not found: {str(e)}")

