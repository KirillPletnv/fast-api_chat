from pydantic import BaseModel, EmailStr, Field

class SOutUser(BaseModel):
    id: int = Field(..., description='ID Пользователя')
    email: EmailStr = Field(..., description='Электронная почта')
    name: str = Field(..., min_length=3, max_length=50, description='Имя, от 3 до 50 знаков')

class SInUserRegister(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    name: str = Field(..., min_length=3, max_length=50, description='Имя, от 3 до 50 знаков')
    password: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')
    password_check: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')



class SInUserAuth(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')