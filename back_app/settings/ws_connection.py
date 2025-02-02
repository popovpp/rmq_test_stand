from fastapi import WebSocket

from back_app.utils.utils import get_local_ip
from back_app.settings.settings import APP_PORT, URL_PREFIX


# WS gate url
WS_GATE_URL = f"ws://{get_local_ip()}:{APP_PORT}{URL_PREFIX}/ws/gate-channel"


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.recv_messsage = ''
        self.test = 'test'

    async def connect(self, order_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[order_id] = websocket

    def disconnect(self, order_id: str):
        self.active_connections.pop(order_id)

    async def send_personal_message(self, message: dict, order_id: str):
        if websocket := self.active_connections.get(order_id):
            self.recv_messsage = ''
            return await websocket.send_json(message)

    async def receive_text(self, order_id: str):
        if websocket := self.active_connections.get(order_id):
            self.recv_messsage = await websocket.receive_text()
            return self.recv_messsage

    def get_recv_message(self):
        return self.recv_messsage


ws_manager = ConnectionManager()
ws_manager_gate = ConnectionManager()
