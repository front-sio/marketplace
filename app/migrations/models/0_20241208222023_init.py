from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "businessowner" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "business_name" VARCHAR(255) NOT NULL,
    "address" TEXT NOT NULL,
    "phone" VARCHAR(50) NOT NULL,
    "email" VARCHAR(50) NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT
);
CREATE TABLE IF NOT EXISTS "category" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS "product" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "price" VARCHAR(40) NOT NULL,
    "quantity" INT NOT NULL  DEFAULT 0,
    "description" TEXT,
    "image" VARCHAR(255),
    "category_id" INT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE,
    "seller_id" INT REFERENCES "businessowner" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "shippingcompany" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "contact" VARCHAR(50) NOT NULL,
    "address" TEXT NOT NULL,
    "user_id" INT
);
CREATE TABLE IF NOT EXISTS "tutorials" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "role" VARCHAR(50) NOT NULL  DEFAULT 'customer',
    "shipping_company_profile_id" INT  UNIQUE REFERENCES "shippingcompany" ("id") ON DELETE CASCADE,
    "business_owner_profile_id" INT  UNIQUE REFERENCES "businessowner" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "order" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "quantity" INT NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'Pending',
    "buyer_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "product_id" INT NOT NULL REFERENCES "product" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "shipping" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "tracking_number" VARCHAR(255) NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'Pending',
    "cost" VARCHAR(40) NOT NULL,
    "order_id" INT NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE,
    "shipping_company_id" INT NOT NULL REFERENCES "shippingcompany" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
