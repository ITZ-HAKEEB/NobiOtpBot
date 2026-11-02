from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["telegram_number_bot"]

users_col = db["users"]
numbers_col = db["numbers"]
orders_col = db["orders"]

async def get_user(user_id: int):
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "balance": 0.0, "terms_accepted": False}
        await users_col.insert_one(user)
    return user

async def update_balance(user_id: int, amount: float):
    await users_col.update_one({"user_id": user_id}, {"$inc": {"balance": amount}}, upsert=True)

async def set_terms_accepted(user_id: int):
    await users_col.update_one({"user_id": user_id}, {"$set": {"terms_accepted": True}}, upsert=True)
  
