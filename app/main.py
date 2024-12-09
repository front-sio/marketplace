from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db, close_db
from app.api import router  # Import the router from the single api.py file
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Include the router defined in api.py
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to frontend URL in production, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)




app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# Register Tortoise ORM with FastAPI
register_tortoise(
    app,
    db_url="sqlite://market_place.sqlite3",  # Ensure this is your actual DB connection string
    modules={"models": ["app.models"]},  # Register models here
    generate_schemas=True,  # Generate schemas automatically
    add_exception_handlers=True,  # Add exception handlers for Tortoise ORM
)
