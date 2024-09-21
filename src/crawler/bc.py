import asyncio
import endpoints
import aiohttp
from typing import Dict
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'protobuf')))
import gtfs_realtime_pb2 as gtfsrt

class BCTransit:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.stops: [Dict[str, str]] = []
        self.buses: [Dict[str, str]] = []
        self.routes: [Dict[str, str]] = []
        self.update()
        
    def close(self) -> None:
        return self.session.close()
        
    def validate_res_status(self, res):
        if res.status // 100 != 2:
            raise RuntimeError(f"BCApi: http request failed: {res.url}")

    def get_buses(self) -> [Dict[str, str]]:
        return self.buses

    def get_stops(self) -> [Dict[str, str]]:
        return self.stops

    def get_routes(self) -> [Dict[str, str]]:
        return self.routes
        
    async def update(self) -> None:
        endpoint_list: [str] = [
            endpoints.BC_BUSES,
            endpoints.BC_ROUTES,
            endpoints.BC_STOPS
        ]
        properties: [str] = [
            "buses",
            "routes",
            "stops",
        ]
        
        async def fetch(url: str) -> Dict[str, str]:
            async with self.session.get(url) as response:
                return await response.json()
            
        json_list = await asyncio.gather(*[fetch(url) for url in endpoint_list], return_exceptions=True)
        
        for i, json in enumerate(json_list):
            setattr(self, properties[i], json)
            
            

async def test_main() -> None:
    try: 
        bc_wrapper: BCTransit = BCTransit()
        await bc_wrapper.update()
        buses: [Dict[str, str]] = bc_wrapper.get_buses()
        for bus in buses:
            print(bus)
        buses: [Dict[str, str]] = bc_wrapper.get_routes()
        for bus in buses:
            print(bus)
    except RuntimeError as e:
        print(f"Error: {e}")
    finally:
        await bc_wrapper.close();
        

if __name__ == "__main__":
    asyncio.run(test_main())
