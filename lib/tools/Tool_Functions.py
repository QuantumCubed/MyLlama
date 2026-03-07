from lib.integrations.home.IoT import HomeAssistantWebSocket

def tool(description: str, parameters: dict | None = None):
    def decorator(func):
        func.tool_definition = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": parameters or {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        return func
    return decorator

class ExternalTools:
    def __init__(self, HA: HomeAssistantWebSocket) -> None:
        self.HA = HA

    def time_now(self) -> str:
        """Get the local time to the user"""
        return "The time is 2:20"
    
    # @tool(
    #     description="Toggle the standup lamp on/off",
    #     parameters={
    #         "type": "object",
    #         "properties": {
    #             "entity_id": {
    #                 "type": "string",
    #                 "description": "The entity ID e.g. switch.standup_lamp"
    #             }
    #         },
    #     "required": ["entity_id"]
    #     }
    # )
    # async def standup_lamp_toggle(self, entity_id: str) -> str:
    #     """Toggle the standup lamp"""
    #     print(entity_id)
    #     message = {
    #         "type": "call_service",
    #         "domain": "switch",
    #         "service": "toggle",
    #         "service_data": {
    #             "entity_id": "switch.standup_lamp"
    #         }
    #     }

    #     response = await self.HA.send(message)

        # return f"success: {response["success"]}"

    @tool(
        description="Turn on all the entities in the area",
        parameters={
            "type": "object",
            "properties": {
                "area_name": {
                    "type": "string",
                    "description": "This function can accept only one area_name. An area_name is the reference from the user to the area_id e.g. living room -> living_room"
                }
            },
        "required": ["area_name"]
        }
    )
    async def area_turn_on(self, area_name: str):
        area = self.HA.ha_areas[area_name]

        req = {
            "type": "call_service",
            "domain": "homeassistant",
            "service": "turn_on",
            "target": {
                "area_id": area["area_id"]
            }
        }

        # ADD ACTUAL STATING CHECKING!!!

        await self.HA.send(req)

        return "{success: true, reason: area state is now on}" # might not always be true; amend later

    @tool(
        description="Turn off all the entities in the area",
        parameters={
            "type": "object",
            "properties": {
                "area_name": {
                    "type": "string",
                    "description": "This function can accept only one area_name. An area_name is the reference from the user to the area_id e.g. living room -> living_room"
                }
            },
        "required": ["area_name"]
        }
    )
    async def area_turn_off(self, area_name: str):
        area = self.HA.ha_areas[area_name]

        req = {
            "type": "call_service",
            "domain": "homeassistant",
            "service": "turn_off",
            "target": {
                "area_id": area["area_id"]
            }
        }

        # ADD ACTUAL STATING CHECKING!!!

        await self.HA.send(req)

        return "{success: true, reason: area state is now off}" # might not always be true; amend later

    @tool(
        description="Turn the given entities off.",
        parameters={
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "This function can accept multiple entity names. An entity name is the reference from the user to the entity_id e.g. standup lamp -> switch.standup_lamp"
                }
            },
        "required": ["entities"]
        }
    )
    async def entity_turn_off(self, entities: list[str]):
        for entity_name in entities:

            entity = self.HA.ha_states[entity_name.lower()]

            print(entity["entity_id"])

            if entity["state"] == "off":
                return "{success: false, reason: light state is already off}"

            req = {
                "type": "call_service",
                "domain": entity["domain"],
                "service": "turn_off",
                "target": {
                    "entity_id": entity["entity_id"]
                }
            }

            await self.HA.send(req)

            return "{success: true, reason: light state is now off}" # might not always be true; amend later

    @tool(
        description="Turn the given entities on.",
        parameters={
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "This function can accept multiple entity names. An entity name is the reference from the user to the entity_id e.g. standup lamp -> switch.standup_lamp"
                }
            },
        "required": ["entities"]
        }
    )
    async def entity_turn_on(self, entities: list[str]):
        for entity_name in entities:

            entity = self.HA.ha_states[entity_name]

            print(entity["entity_id"])

            if entity["state"] == "on":
                return "{success: false, reason: light state is already on}"

            req = {
                "type": "call_service",
                "domain": entity["domain"],
                "service": "turn_on",
                "target": {
                    "entity_id": entity["entity_id"]
                }
            }

            await self.HA.send(req)

            return "{success: true, reason: light state is now on}" # might not always be true; amend later    
