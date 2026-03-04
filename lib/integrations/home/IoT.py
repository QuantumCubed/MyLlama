import asyncio
import os
import json
import websockets

class HomeAssistantWebSocket:
    def __init__(self) -> None:
        self.url = os.environ.get("HomeAssistant_Endpoint")
        self.token = os.environ.get("HomeAssistant_Token")
        self._ws = None
        self.ha_states = {}
        self._msg_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._listener_task = None
 
    
    def _next_id(self):
        self._msg_id += 1
        return self._msg_id

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

            # Init WebSocket listener
            
            self._listener_task = asyncio.create_task(self._listen())

            # RACE CONDITION HERE, WILL DEAL LATER!!!

            init_state_res = await self.send({"type": "get_states"})

            if not init_state_res["success"]:
                raise Exception("Unable To Load HomeAssistant States!")

            self.ha_states = {state["entity_id"]: state for state in init_state_res["result"]}

            print("Home Assistant Initialization States Configured!")

            event_subscription = await self.send({"type": "subscribe_events", "event_type": "state_changed"})

            if not event_subscription["success"]:
                raise Exception("Unable To Establish HomeAssistant State Subscription!")
            
            print("Home Assistant Event Subscription Established!")
            
        except Exception as e:
            raise e

    async def send(self, message: dict) -> dict:

        if not self.ws:
            raise Exception("No WebSocket Connection!")

        msg_id = self._next_id()
        message["id"] = msg_id

        # register future for listener

        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._pending[msg_id] = future
        
        await self.ws.send(json.dumps(message))

        return await future # json.loads(await self.ws.recv())
    
    async def _listen(self):
        async for raw in self.ws:
            data: dict = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "result":
                future = self._pending.pop(data["id"], None)
                if future and not future.done():
                    future.set_result(data)
            elif msg_type == "event":
                self._handle_event(data["event"])
    
    def _handle_event(self, event: dict):
        if event.get("event_type") != "state_changed":
            return
        
        new_state = event["data"].get("new_state")
        entity_id = event["data"]["entity_id"]

        if new_state:
            self.ha_states[entity_id] = new_state
            # print(f"EntitiyID: {entity_id}, State: {new_state}")
        else:
            # new_state is None means the entity was removed
            self.ha_states.pop(entity_id, None)
    
    async def disconnect(self):
        if self._listener_task:
                self._listener_task.cancel()
                try:
                    await self._listener_task
                except asyncio.CancelledError:
                    pass  # expected
        if self.ws:
            await self.ws.close()
