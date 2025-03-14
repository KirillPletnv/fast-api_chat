from typing import Annotated
from fastapi import  APIRouter, Depends, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UserDAO
from app.users.dependensies import get_current_user_dependence
from app.users.models import User
from app.users.schemas import SInUserAuth, SInUserRegister, SOutUser


users_api_router = APIRouter(prefix='/api_v1/users', tags=['Users'])
auth_api_router = APIRouter(prefix='/api_v1/auth', tags=['Auth'])




@auth_api_router.post('/register/')
async def register_user(user_data: SInUserRegister) -> dict:
    user: User = await UserDAO.find_one_or_none(email=user_data.email)

    if user:
        raise UserAlreadyExistException
    
    if user_data.password != user_data.password_check:
        raise PasswordMismatchException
    
    hashed_password = get_password_hash(user_data.password)
    
    await UserDAO.add(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    return {'message': 'Вы успешно зарегистрированы'}


@auth_api_router.post('/login/')
async def auth_user(response: Response, user_data: SInUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({'sub': str(check.id)})
    response.set_cookie(key='user_access_token', value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Успешная авторизация'}


@auth_api_router.post('/logout/')
async def logout_user(response: Response):
    response.delete_cookie(key='user_access_token')
    return {'message': 'Пользователь успешно вышел из системы'}


@users_api_router.get('/me', response_model=SOutUser, description='В случае если пользователь авторизован возвращает имя и email, в противном случае исключение')
async def get_me(user: Annotated[User, Depends(get_current_user_dependence)]):

    return user

@users_api_router.get('/all_interlocutors', response_model=list[SOutUser], description='В случае если пользователь авторизован возвращает список всех собеседников')
async def get_all_interlocutors(user: Annotated[User, Depends(get_current_user_dependence)]):

    return await UserDAO.find_all_except_user(user)

