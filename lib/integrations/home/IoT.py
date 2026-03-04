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
        self.ha_areas = {}
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

            await self.ha_properties_init()
            
        except Exception as e:
            raise e
        
    async def ha_properties_init(self):
        try:
            init_area_res = await self.send({"type": "config/area_registry/list"})
            init_device_res = await self.send({"type": "config/device_registry/list"})
            init_entity_res = await self.send({"type": "config/entity_registry/list"})
            init_state_res = await self.send({"type": "get_states"})

            if not init_area_res["success"]: raise Exception("Unable To Load HA Areas!")
            if not init_device_res["success"]: raise Exception("Unable To Load HA Devices!")
            if not init_entity_res["success"]: raise Exception("Unable To Load HA Entities!")
            if not init_state_res["success"]: raise Exception("Unable To Load HA States!")

            area_lookup = {a["area_id"]: a["name"] for a in init_area_res["result"]}
            device_lookup = {d["id"]: d["area_id"] for d in init_device_res["result"]}
            entity_lookup = {e["entity_id"]: e for e in init_entity_res["result"]}

            def resolve_area(entity: dict) -> str | None:
                area_id = entity.get("area_id") or device_lookup.get(entity.get("device_id"))
                return area_lookup.get(area_id)

            self.ha_states = {
                state["attributes"].get("friendly_name", state["entity_id"]).lower(): {
                    "domain": state["entity_id"].split(".")[0],
                    "entity_id": state["entity_id"],
                    "area": resolve_area(entity_lookup.get(state["entity_id"], {})),
                    "state": state
                }
                for state in init_state_res["result"]
            }

            self.ha_areas = {
                (area.get("aliases") or [area["name"]])[0].lower(): {
                    "area_id": area["area_id"],
                    "entities": [e for e in self.ha_states if self.ha_states[e].get("area") == area["name"]]
                }
                for area in init_area_res["result"]
            }

            print("Home Assistant Initialization States Configured!")

            # print(self.ha_states)
            print("AREA REGISTRY:", self.ha_areas)

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
        
        entity_id = event["data"]["entity_id"]
        new_state = event["data"].get("new_state")
        
        if new_state:
            name = new_state["attributes"].get("friendly_name") or entity_id
            if name in self.ha_states:
                self.ha_states[name]["state"] = new_state
            # print(f"EntitiyID: {entity_id}, State: {new_state}")
        else:
            # entity removed — need to find and pop by entity_id
            # O(n) REMOVAL CASE: either add index dictionary or somethin else idk
            
            name = next((n for n, s in self.ha_states.items() if s["entity_id"] == entity_id), None)
            if name:
                self.ha_states.pop(name)
    
    async def disconnect(self):
        if self._listener_task:
                self._listener_task.cancel()
                try:
                    await self._listener_task
                except asyncio.CancelledError:
                    pass  # expected
        if self.ws:
            await self.ws.close()
