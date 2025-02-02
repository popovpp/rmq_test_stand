import asyncio
from websockets.asyncio.server import serve


def sync_singl_def(singl_def, def_params=[]):

    try:
        result = asyncio.run(singl_def(*def_params))
        print(result)
    except Exception as error:
        print(error)
        print(str(error))


async def ws_server(host, port, handler):

    while True:
        server = await serve(handler, host=host, port=port, max_size=100048576)
        await server.serve_forever()
