import asyncio
import endpoints
import aiohttp
from typing import Dict

class BCApi:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    def validate_res_status(self, res):
        if res.status // 100 != 2:
            raise RuntimeError(f"BCApi: http request failed: {res.url}")
        
    def close(self) -> None:
        return self.session.close()

    async def get_buses(self) -> [Dict[str, str]]:
        async with self.session.get(endpoints.BC_BUSES) as response:
            self.validate_res_status(response)

            json = await response.json()
            return [j for j in json]

    async def get_routes(self) -> [Dict[str, str]]:
        async with self.session.get(endpoints.BC_ROUTES) as response:
            self.validate_res_status(response)

            json = await response.json()
            return [j for j in json]

async def main() -> None:
    try: 
        bc_wrapper: BCApi = BCApi()
        buses: [Bus] = await bc_wrapper.get_buses()
        for bus in buses:
            print(bus)
    except e:
        print(f"Error: {e}")
    finally:
        await bc_wrapper.close();
        

if __name__ == "__main__":
    asyncio.run(main())
