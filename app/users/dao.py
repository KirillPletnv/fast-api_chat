from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker
from sqlalchemy import select

class UserDAO(BaseDAO):
    model = User
    
    @classmethod
    async def find_all_except_user(cls, user: User):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id != user.id)
            result = await session.execute(query)
            return result.scalars().all()
    