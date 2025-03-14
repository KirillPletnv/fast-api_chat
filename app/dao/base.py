from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sa_update, delete as sa_delete, func
from app.database import async_session_maker, Base

class BaseDAO:
    model: Base
    
    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
        return result.scalar_one_or_none()
        
        
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
        return result.scalars().all()
        
        
    # @classmethod
    # async def add(cls, **values):
    #     async with async_session_maker() as session:
            
    #         async with session.begin():
    #             new_instance = cls.model(**values)
    #             session.add(new_instance)
    #             print(f'async def add(cls, **values): new_instance.id: {new_instance.id}')
    #             # _cub_custom(new_instance)
    #             # try:
    #             #     print(f'async def add(cls, **values): new_instance.sender_id: {new_instance.sender_id}')
    #             #     await session.commit()
    #             #     print(f'async def add(cls, **values): new_instance.id: {new_instance.id}')
    #             # except Exception as e:
    #             #     await session.rollback()
    #             #     raise e
                
    #     return new_instance

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                # await session.commit()
        # async with session.begin():
        #     new_instance = cls.model(**values)
        #     session.add(new_instance)
        #     print(f'async def add(cls, **values): new_instance.id: {new_instance.id}')
            # _cub_custom(new_instance)
            # session.begin()
            # async with session.begin():
            #     try:                    
            #     print(f'async def add(cls, **values): new_instance.id: {new_instance.id}')
            #     print(f'async def add(cls, **values): new_instance.sender_id: {new_instance.sender_id}')
            #     await session.commit()
            #     print(f'async def add(cls, **values): new_instance.id: {new_instance.id}')
            #     raise Exception()
            # except Exception as e:
            #     await session.rollback()
            #     raise e
                
        return new_instance



    # @classmethod
    # def