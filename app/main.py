from fastapi import FastAPI, Request, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.exceptions import TokenExpiredException, TokenNotFoundException
# from app.chat.router import router as chat_router
from simple_py_config import Config

config = Config()
config.from_dot_env_file('./.env')

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

from app.users.dependensies import get_current_user_id_dependence
from app.users.router import auth_api_router, users_api_router
app.include_router(auth_api_router)
app.include_router(users_api_router)
# app.include_router(chat_router)

from app.pages.router import router as page_router
app.include_router(page_router)


from app.chat.router import api_chat_router
app.include_router(api_chat_router)

# from app.websocket import ws_router
# app.include_router(ws_router)

# @app.get('/')
# async def redirect_to_auth():
#     return RedirectResponse(url='/auth')

# @app.exception_handler(TokenExpiredException)
# async def token_expired_exception_handler(
#     request: Request, 
#     exc: HTTPException
#     ):
#     return RedirectResponse(url='/auth')

# @app.exception_handler(TokenNotFoundException)
# async def token_not_found_exception_handler(
#     request: Request,
#     exc: HTTPException
#     ):
#     return RedirectResponse('/auth')




from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse

# app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://5.35.108.213:8080/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""



from app.websocket import manager

@app.websocket("/ws/connect")
# app.websocket('/ws/connect')
async def websocket_endpoint(*,
    websocket: WebSocket, user_id: int):
    print(f'async def websocket_endpoint(websocket: WebSocket, user_id: int): pre')
    await manager.connect(user_id, websocket)
    print(f'async def websocket_endpoint(websocket: WebSocket, user_id: int): past')
    try:
        while True:
            # mes = await websocket.receive()
            mes = await websocket.receive_text()
            if mes == 'close':
                await websocket.close()
                manager.disconnect(user_id, websocket)
                break
            # websocket
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


