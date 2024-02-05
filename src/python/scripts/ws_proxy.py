# Websocket proxy to log traffic between web3 and the wallet extension. Note this doesn't work with the token
# as a parameter (i.e. need to use https://testnet.ten.xyz/v1/<token> and not with ?token=<token>)
#
import argparse, asyncio, websockets, sys


async def hello(websocket, path):
    """Called whenever a new connection is made to the server."""

    url = REMOTE_URL + path
    async with websockets.connect(url) as ws:
        taskA = asyncio.create_task(clientToServer(ws, websocket))
        taskB = asyncio.create_task(serverToClient(ws, websocket))

        await taskA
        await taskB


async def clientToServer(ws, websocket):
    async for message in ws:
        FP.write('%s\n' % message)
        FP.flush()
        await websocket.send(message)


async def serverToClient(ws, websocket):
    async for message in websocket:
        FP.write('%s\n' % message)
        FP.flush()
        await ws.send(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='websocket proxy.')
    parser.add_argument('--host', help='Host to bind to')
    parser.add_argument('--port', help='Port to bind to')
    parser.add_argument('--remote_url', help='Remote websocket url')
    parser.add_argument('--filename', help='Log messages to this filename')
    args = parser.parse_args()

    REMOTE_URL = args.remote_url
    sys.stdout.write('Connection to remote url %s' % REMOTE_URL)
    sys.stdout.flush()
    FP = open(args.filename, 'w')

    start_server = websockets.serve(hello, args.host, args.port)
    sys.stdout.write('Connection bound and listening')
    sys.stdout.flush()

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()