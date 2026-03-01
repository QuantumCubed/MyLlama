import os
import json
import websockets

class HomeAssistantWebSocket:
    def __init__(self) -> None:
        self.url = os.environ.get("HomeAssistant_Endpoint")
        self.token = os.environ.get("HomeAssistant_Token")
        self.ws = None
        self.message_id = 0

    async def connect(self) -> None:

        try:
            if not self.url or not self.token:
                raise Exception("URL/TOKEN Unavailable!")
            
            self.ws = await websockets.connect(self.url)

            await self.ws.recv()

            # complete handshake with auth

            await self.ws.send(json.dumps({
                "type": "auth",
                "access_token": self.token
            }))

            auth_conf = json.loads(await self.ws.recv())
            if auth_conf["type"] != "auth_ok":
                raise Exception("Authentication Failed!")
            
            print("Home Assistant WebSocket Connection Established!")
            
        except:
            Exception("Unknown Connection Error!")

    async def send(self, message: dict) -> dict:

        if not self.ws:
            raise Exception("No WebSocket Connection!")

        self.message_id += 1

        message["id"] = self.message_id
        
        await self.ws.send(json.dumps(message))

        return json.loads(await self.ws.recv())
    
    async def disconnect(self):
        if self.ws:
            await self.ws.close()
