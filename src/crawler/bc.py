import asyncio

import aiohttp


class BC:
    def __init__(self):
        pass

    async def poll(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://python.org") as response:
                print("Status:", response.status)
                print("Content-type:", response.headers["content-type"])

                html = await response.text()
                print("Body:", html[:15], "...")

async def main() -> None:
    a: BC = BC()
    await a.poll()

if __name__ == "__main__":
    asyncio.run(main())
