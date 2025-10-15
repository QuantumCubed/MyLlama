from datetime import tzinfo, datetime
from pydantic import validate_call
import lib.integrations.IoT as IOT

# @validate_call
# def get_local_time(format: str, timezone: tzinfo | None) -> str:
#     # return "5:35 AM"
#     return str(datetime.now(timezone))

@validate_call
def get_local_time(format: str, timezone: str | None) -> str:
    return "5:35 AM"

@validate_call
async def turn_lights_off():
    await IOT.lights_off()
    return "Lights Off!"

@validate_call
async def turn_lights_on():
    await IOT.lights_on()
    return "Lights On!"
