import os
from dotenv import load_dotenv
import httpx
import asyncio

# load_dotenv()

HUE_BASE_URL = "https://{}/api/{}/".format(os.environ.get("HUE_IP"), os.environ.get("HUE_AUTH_USER"))

async def get_light_info():
    async with httpx.AsyncClient(verify=False) as myLlama:
        response = await myLlama.get(HUE_BASE_URL + "lights/2")
        print(response)
        print(str(response.content))

async def lights_off():
    async with httpx.AsyncClient(verify=False) as myLlama:
        response = await myLlama.put(HUE_BASE_URL + "lights/2/state", json={"on":False})
        print(response)
        print(str(response.content))

async def lights_on():
    async with httpx.AsyncClient(verify=False) as myLlama:
        response = await myLlama.put(HUE_BASE_URL + "lights/2/state", json={"on":True})
        print(response)
        print(str(response.content))

# asyncio.run(lights_on())