"""VRKnock WebSocket Client"""
import _thread
from asyncio.locks import Event
import threading
import time
import websocket
import asyncio
import json

from custom_components.vrknock_client.const import VERSION

PORT = 16945


class VRKnockClient:
    def __init__(self, host: str, code: str, mode: str = "direct") -> None:
        """VRKnock WebSocket Client"""
        self._host = host
        self._code = code
        self._mode = mode
        self._socket = None
        self._latest_status = None
        self._socket_future = threading.Event()
        self._status_future = threading.Event()

    def on_message(self, ws, message):
        print("on_message")
        print(message)
        data = json.loads(message)
        data["_time"] = time.time()
        if data["evt"] == "status":
            self._latest_status = data
            self._status_future.set()

    def on_error(self, ws, error):
        print("on_error")
        print(error)
        self._socket = ws
        self._socket_future.set()

    def on_close(self, ws, close_status_code, close_msg):
        print("on_close")
        print(close_msg)
        self._socket = ws
        self._socket_future.set()
        self._latest_status = None
        self._status_future.set()

    def on_open(self, ws):
        print("on_open")
        self._socket = ws
        self._socket_future.set()
        print("socket future set")

    def open_socket(self):
        print("open_socket")
        self._socket = None
        self._socket_future.clear()
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            f"ws://{self._host}:{PORT}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws.run_forever()
        return ws

    def close_socket(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None
        self._socket_future.clear()
        self._latest_status = None
        self._status_future.clear()

    async def get_socket(self):
        print("get_socket")
        if (
            self._socket is not None
            and self._socket is not None
            and self._socket.sock is not None
            and self._socket.sock.connected
        ):
            return self._socket

        def background():
            self.open_socket()
            print("socket created")

        thread = threading.Thread(target=background)
        thread.start()
        print("started thread")

        self._socket_future.wait()
        print("got socket!!")
        return self._socket

    async def _send(self, message: str):
        print("_send")
        print(message)
        ws = await self.get_socket()
        ws.send(message)

    async def send(self, message: str):
        print("send")
        await self._send(message)

    async def send_json(self, obj: any):
        print("send_json")
        print(obj)
        obj["code"] = self._code
        obj["platform"] = "homeassistant"
        obj["version"] = VERSION
        await self.send(json.dumps(obj))

    async def query_status(self):
        print("query_status")

        await self.send_json({"action": "status", "code": self._code})

    def get_latest_status(self):
        return self._latest_status

    async def get_status(self):
        self._status_future.clear()
        await self.query_status()
        self._status_future.wait()
        return self.get_latest_status()

    async def trigger_knock(self, message: str):
        print("trigger_knock")

        await self.send_json(
            {"action": "triggerKnock", "code": self._code, "message": message}
        )
