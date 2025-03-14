from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import  datetime, timezone
from app.exceptions import TokenNotFoundException, UserNoteFoundException, NoJwtException, NoUserIdException, TokenExpiredException
from app.users.dao import UserDAO
from simple_py_config import Config

from app.users.models import User

config: Config = Config.get_instance()


def get_token_dependence(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise TokenNotFoundException()
    return token


async def get_current_user_dependence(token: Annotated[str, Depends(get_token_dependence)]) -> User:
    try:
        payload = jwt.decode(
            token, 
            config.get('SECRET_KEY'), 
            config.get('ALGORITHM')
            )
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise NoJwtException
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException
    
    user = await UserDAO.find_one_or_none_by_id(int(user_id))
    if not user:
        raise UserNoteFoundException
    return user


async def get_current_user_id_dependence(user: Annotated[User, Depends(get_current_user_dependence)]) -> int:
    return user.id


# async def get_current_user(request: Request) -> User:
#     token = get_token_dependence(request)
#     return await get_current_user_dependence(token)
    

