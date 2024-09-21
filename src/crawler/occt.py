import aiohttp
import asyncio

class OCCT()
    def __init__(self):
        pass

    async def poll(self):
        async with aiohttp.ClientSession as session:
            async with session.get("http://my.binghamton.edu") as response:
                print("Chistophir Binghamton Status: ", response)
                print("HackBU Organizer Content-type: ", response.headers['content-type'])

                html = await response.txt()
                print("A Train Body: ", html[:15], "...")