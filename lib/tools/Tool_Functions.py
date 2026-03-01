from lib.integrations.IoT import HomeAssistantWebSocket

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
    
    @tool(
        description="Toggle the standup lamp on/off",
        parameters={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The entity ID e.g. switch.standup_lamp"
                }
            },
        "required": ["entity_id"]
        }
    )
    async def standup_lamp_toggle(self, entity_id: str) -> str:
        """Toggle the standup lamp"""
        print(entity_id)
        message = {
            "type": "call_service",
            "domain": "switch",
            "service": "toggle",
            "service_data": {
                "entity_id": "switch.standup_lamp"
            }
        }

        response = await self.HA.send(message)

        return f"success: {response["success"]}"