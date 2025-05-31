import asyncio
import json
import os
from datetime import datetime
import websockets

# Constants
DATA_FILE = "storage.json"
WS_URL = "wss://websocket.layeredge.io/ws/node?token={}"
MAX_RECONNECTS = 5

# Globals
storage = {}
ws = None
is_connected = False
reconnect_attempts = 0
heartbeat_task = None


# Storage Management
def load_storage():
    global storage
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            storage = json.load(f)
    else:
        storage = {}


def save_storage():
    with open(DATA_FILE, "w") as f:
        json.dump(storage, f, indent=2)


def get_item(key, fallback=None):
    return storage.get(key, fallback)


def set_item(key, value):
    storage[key] = value
    save_storage()


def remove_item(key):
    if key in storage:
        del storage[key]
        save_storage()


# Connection Utilities
async def update_status(status):
    set_item("connectionStatus", status)
    print(f"[STATUS] {status}")
    if status == "Disconnected":
        now = datetime.utcnow().isoformat()
        set_item("lastDisconnected", now)


async def heartbeat():
    while is_connected and ws and ws.open:
        try:
            await send_node_command("Heartbeat")
        except Exception as e:
            print("Heartbeat error:", e)
        await asyncio.sleep(25)


async def connect_ws(token):
    global ws, is_connected, reconnect_attempts, heartbeat_task

    await disconnect_ws()
    await update_status("Connecting...")

    try:
        headers = {
            "Host": "websocket.layeredge.io",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Upgrade": "websocket",
            "Origin": "chrome-extension://fnjlbckpopjmpgkjgoiegmnnhahegbcb",
            "Sec-WebSocket-Version": "13",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
        }

        ws = await websockets.connect(
            WS_URL.format(token),
            extra_headers=headers
        )
        is_connected = True
        reconnect_attempts = 0
        print("Connected to WebSocket.")

        await update_status("Connected successfully!")

        if heartbeat_task:
            heartbeat_task.cancel()
        heartbeat_task = asyncio.create_task(heartbeat())

        await listen_messages()

    except Exception as e:
        is_connected = False
        await update_status(f"Connection failed: {e}")
        if reconnect_attempts < MAX_RECONNECTS:
            reconnect_attempts += 1
            delay = min(2 ** reconnect_attempts, 30)
            print(f"Reconnecting in {delay}s... (Attempt {reconnect_attempts}/{MAX_RECONNECTS})")
            await asyncio.sleep(delay)
            await connect_ws(token)


async def listen_messages():
    global ws, is_connected
    try:
        async for message in ws:
            print("[Message]", message)
            await handle_message(message)
    except Exception as e:
        print("Connection lost:", e)
    finally:
        is_connected = False
        await update_status("Disconnected")


async def handle_message(message):
    try:
        data = json.loads(message)
        msg_type = data.get("type", "")
        if msg_type == "connected":
            print("[✓] Connected acknowledged")
        elif msg_type == "heartbeat_ack":
            print("[♥] Heartbeat acknowledged")
        elif msg_type == "NodeUpdate":
            print("[↻] Node status updated")
        elif msg_type == "PointsUpdate":
            print("[+] Points updated")
        else:
            print("[?] Unknown message type")
    except Exception as e:
        print("Failed to process message:", e)


async def send_node_command(command_type):
    if not ws or not ws.open:
        return {"success": False, "error": "WebSocket not connected"}

    try:
        msg = json.dumps({"type": command_type})
        await ws.send(msg)
        print(f"[SEND] {msg}")
        return {"success": True}
    except Exception as e:
        print(f"Error sending command '{command_type}': {e}")
        return {"success": False, "error": str(e)}


async def disconnect_ws():
    global ws, is_connected
    if ws:
        await ws.close()
        ws = None
    is_connected = False
    await update_status("Disconnected")


async def main():
    load_storage()
    token = get_item("wsToken")

    if not token:
        token = input("Enter wsToken: ").strip()
        set_item("wsToken", token)

    await connect_ws(token)


if __name__ == "__main__":
    asyncio.run(main())
