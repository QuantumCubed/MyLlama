from lib.integrations.IoT import HomeAssistantWebSocket

class ExternalTools:
    def __init__(self, HA: HomeAssistantWebSocket) -> None:
        self.HA = HA

    def time_now(self) -> str:
        """Get the local time to the user"""
        return "The time is 2:20"

    async def standup_lamp_toggle(self) -> str:
        """Toggle the standup lamp"""
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