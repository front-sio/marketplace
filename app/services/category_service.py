from fastapi import HTTPException
from app.models import Category

# Function to create a new category
async def create_category(name: str):
    # Check if category already exists
    existing_category = await Category.get_or_none(name=name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    # Create new category
    category = await Category.create(name=name)
    return category

# Function to get a category by ID
async def get_category_by_id(category_id: int):
    try:
        category = await Category.get(id=category_id)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Category does not exist")
    return category

# Function to get all categories
async def get_all_categories():
    categories = await Category.all()
    return categories
