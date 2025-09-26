from datetime import datetime
from database.mongo import mongo

class UserRepository:
    def __init__(self):
        self.users      = mongo.db.users
        self.temp_user  = mongo.db.members
        self.perm_v1    = mongo.db.perm_v1
        self.perm_v2    = mongo.db.perm_v2

    async def add_user(self, user_id: int) -> None:
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"user_id": user_id}},
                upsert=True
            )

    async def remove_user(self, user_id: int) -> None:
        user = await self.users.find_one({"user_id": user_id})
        if user:
            await self.users.delete_one({"user_id": user_id})

    async def add_temp_user(self, user_id: int, expiry: datetime) -> None:
        await self.temp_user.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "expiry": expiry}},
            upsert=True
        )
    
    async def remove_temp_user(self, user_id: int) -> None:
        user = await self.temp_user.find_one({"user_id": user_id})
        if user:
            await self.temp_user.delete_one({"user_id": user_id})

    async def add_perm_v1(self, user_id: int) -> None:
        await self.perm_v1.update_one(
            {"user_id": user_id},
            {"$set": {
                    "user_id": user_id
                }
            },
            upsert=True
        )
    
    async def remove_perm_v1(self, user_id: int) -> None:
        user = await self.perm_v1.find_one({"user_id": user_id})
        if user:
            await self.perm_v1.delete_one({"user_id": user_id})
    
    
    async def add_perm_v2(self, user_id: int) -> None:
        await self.perm_v2.update_one(
            {"user_id": user_id},
            {"$set": {
                    "user_id": user_id
                }
            },
            upsert=True
        )
    
    async def remove_perm_v2(self, user_id: int) -> None:
        user = await self.perm_v2.find_one({"user_id": user_id})
        if user:
            await self.perm_v2.delete_one({"user_id": user_id})
    
class PromoRepository:
    def __init__(self):
        self.promo = mongo.db.promo