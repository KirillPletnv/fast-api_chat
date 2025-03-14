from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, time, timedelta, timezone
from simple_py_config import Config
from app.users.dao import UserDAO
from app.users.models import User


config: Config = Config.get_instance()
PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')



def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=float(config.get('TOKEN_EXPIRE_DAYS')))
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, key=config.get('SECRET_KEY'), algorithm=config.get('ALGORITHM'))
    return encode_jwt


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

async def authenticate_user(email: EmailStr, password: str) -> User | None:
    user: User = await UserDAO.find_one_or_none(email=email)
    
    # print(f'in authenticate_user: user {user}')
    
    if not user or not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None
    return user