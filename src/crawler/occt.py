import aiohttp
import asyncio
import endpoints
import json


class OCCT:
    def __init__(self):
        self.VehicleData = {}
        self.RouteData = {}
        self.ServiceData = {}
        pass

    def checkVehicles(self, vehicleDict):
        for i, vehicle in enumerate(vehicleDict):
            if vehicle["tripID"] is None:
                vehicleDict[i] = None
                # print(vehicle)
        return vehicleDict

    async def pollVehicles(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoints.OCCT_VEHICLES) as vehicleResponse:
                jsonOCCTVEHICLES = await vehicleResponse.json()
                self.VehicleData = self.checkVehicles(jsonOCCTVEHICLES["get_vehicles"])
                # print(self.VehicleData)
        return self.VehicleData

    async def pollRoutes(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoints.OCCT_ROUTES) as routeResponse:
                jsonOCCTRoutes = await routeResponse.json()
                self.RouteData = jsonOCCTRoutes["get_routes"]

        return self.RouteData

    async def pollService(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                endpoints.OCCT_SERVICE_ANNOUNCEMENTS
            ) as serviceResponse:
                jsonOCCTService = await serviceResponse.json()
                self.ServiceData = jsonOCCTService["get_service_announcements"]

        return self.ServiceData

    async def pollAll(self) -> None:
        await self.pollVehicles()
        await self.pollRoutes()
        await self.pollService()


async def main() -> None:
    occt_wrapper: OCCT = OCCT()
    await occt_wrapper.pollAll()


if __name__ == "__main__":
    asyncio.run(main())
