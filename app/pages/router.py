from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.users.dependensies import get_current_user_dependence, get_token_dependence
from app.users.models import User



templates = Jinja2Templates(directory='app/templates')
router = APIRouter(prefix='/chat', tags=['Фронтэнд'])

@router.get('/register', response_class=HTMLResponse)
async def get_register_html(request: Request):
    return templates.TemplateResponse(
        name='reg.html',
        context={'request': request}
    )


@router.get('/login', response_class=HTMLResponse)
async def get_login_html(request: Request):
    return templates.TemplateResponse(
        name='log.html',
        context={'request': request}
    )


@router.get('', response_class=HTMLResponse)
async def get_chat_html(request: Request):

    # try:
    #     token = get_token_dependence(request)
    #     user = await get_current_user_dependence(token)
    # except Exception as e:
    #     return RedirectResponse(
    #         '/chat/login',
    #         status_code=status.HTTP_307_TEMPORARY_REDIRECT
    #     )

    return templates.TemplateResponse(
        name='chat.html',
        context={
            'request': request,
            # 'user': user
            }
    )

