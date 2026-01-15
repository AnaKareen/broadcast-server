import asyncio
import websockets
import sys

HOST = "localhost"
PORT = 8765

connected_clients = set()

async def handle_client(websocket):
    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")

    try:
        async for message in websocket:
            print(f"Received: {message}")
            await broadcast(message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    finally:
        connected_clients.remove(websocket)
        print(f"Clients remaining: {len(connected_clients)}")

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(
            *(client.send(message) for client in connected_clients)
        )

async def start_server():
    print(f"Server running on ws://{HOST}:{PORT}")
    async with websockets.serve(handle_client, HOST, PORT):
        await asyncio.Future()  # Run forever

async def start_client():
    uri = f"ws://{HOST}:{PORT}"
    async with websockets.connect(uri) as websocket:
        print("Connected to server. Type messages and press Enter.\n")

        async def send_messages():
            while True:
                msg = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
                await websocket.send(msg)

        async def receive_messages():
            async for message in websocket:
                print(f"\nBroadcast: {message}\n> ", end="")

        await asyncio.gather(send_messages(), receive_messages())

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python broadcast_server.py start")
        print("  python broadcast_server.py connect")
        return

    command = sys.argv[1]

    if command == "start":
        asyncio.run(start_server())
    elif command == "connect":
        asyncio.run(start_client())
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
