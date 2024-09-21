import aiohttp
import asyncio
import endpoints
import json


class OCCT:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.VehicleData = {}
        self.RouteData = {}
        self.ServiceData = {}

        self.protoBufData = {"Vehicle", "TripUpdate", "Alerts"}
        self.update()
        pass

    def close(self) -> None:
        return self.session.close()

    async def update(self) -> None:
        endpoint_list: [str] = [
            endpoints.OCCT_VEHICLES,
            endpoints.OCCT_ROUTES,
            endpoints.OCCT_SERVICE_ANNOUNCEMENTS,
        ]
        properties: [str] = [
            "VehicleData",
            "RouteData",
            "ServiceData",
        ]

        async def fetch(url):
            async with self.session.get(url) as response:
                self.validate_res_status(response)
                return await response.json()

        json_list = await asyncio.gather(
            *[fetch(url) for url in endpoint_list], return_exceptions=True
        )

        for index, json in enumerate(json_list):
            setattr(self, properties[index], json)

        self.VehicleData = self.checkVehicles(self.VehicleData)

    def validate_res_status(self, res):
        if res.status // 100 != 2:
            raise RuntimeError(f"OCCTApi: http request failed: {res.url}")

    def checkVehicles(self, vehicleDict):
        for i, vehicle in enumerate(vehicleDict):
            if vehicle["tripID"] is None:
                vehicleDict[i] = None
                # print(vehicle)
        return vehicleDict

    def get_buses(self):
        return self.VehicleData

    def get_stops(self):
        return self.ServiceData

    def get_routes(self):
        return self.ServiceData

    # async def pollVehicles(self) -> None:
    #     async with self.session.get(endpoints.OCCT_VEHICLES) as vehicleResponse:
    #         self.validate_res_status(vehicleResponse)

    #         jsonOCCTVEHICLES = await vehicleResponse.json()
    #         self.VehicleData = self.checkVehicles(jsonOCCTVEHICLES["get_vehicles"])
    #         # print(self.VehicleData)
    #     return self.VehicleData

    # async def pollRoutes(self) -> None:
    #     async with self.session.get(endpoints.OCCT_ROUTES) as routeResponse:
    #         self.validate_res_status(routeResponse)

    #         jsonOCCTRoutes = await routeResponse.json()
    #         self.RouteData = jsonOCCTRoutes["get_routes"]

    #     return self.RouteData

    # async def pollService(self) -> None:
    #     async with self.session.get(
    #         endpoints.OCCT_SERVICE_ANNOUNCEMENTS
    #     ) as serviceResponse:
    #         self.validate_res_status(serviceResponse)

    #         jsonOCCTService = await serviceResponse.json()
    #         self.ServiceData = jsonOCCTService["get_service_announcements"]

    #     return self.ServiceData

    # async def pollAll(self) -> None:
    #     await self.pollVehicles()
    #     await self.pollRoutes()
    #     await self.pollService()

    # async def getVehicleInfo(self) -> None:
    #     await self.pollVehicles()


async def main() -> None:
    try:
        occt_wrapper: OCCT = OCCT()
        await occt_wrapper.update()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await occt_wrapper.close()


if __name__ == "__main__":
    asyncio.run(main())
