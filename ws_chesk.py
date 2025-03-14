import asyncio

# from websockets_proxy import Proxy, proxy_connect
from websockets import connect
from simple_py_config import Config

conf = Config()
conf.from_dot_env_file('./.env')


CHECKER_URL = 'ws://5.35.108.213:8080/ws/connect'


async def main():
    print('in async def main():')
    async with connect(CHECKER_URL) as ws:
        async for msg in ws:
            ip_no_proxy = msg
            print("Your IP:", ip_no_proxy)
    print('.')


if __name__ == "__main__":
    asyncio.run(main())