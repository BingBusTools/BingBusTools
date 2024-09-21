import asyncio
import endpoints
import aiohttp
from typing import Dict, Union, List
import sys, os
import logging
import time
sys.path.append("..")
from protobuf.gtfs_realtime_pb2 import FeedMessage, FeedHeader, FeedEntity
import google.protobuf.message as pbm


class BCTransit:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.vehicle_positions: FeedMessage = FeedMessage()
        self.trip_update: FeedMessage = FeedMessage()
        self.alert: FeedMessage = FeedMessage()

    def close(self) -> None:
        return self.session.close()

    def validate_res_status(self, res):
        if res.status // 100 != 2:
            raise RuntimeError(f"BCApi: http request failed: {res.url}")
    
    def __vehicle_json_to_pb(self, vjson: Dict[str, str], out_entity: FeedEntity):
            out_entity.id = str(vjson["id"])
            out_entity.vehicle.position.latitude = float(vjson["lat"])
            out_entity.vehicle.position.longitude = float(vjson["lon"])
    
    def __(self, vjson: Dict[str, str], out_entity: FeedEntity):
            out_entity.id = str(vjson["id"])
            out_entity.vehicle.position.latitude = float(vjson["lat"])
            out_entity.vehicle.position.longitude = float(vjson["lon"])
    
    def update_vehicle_pos_feed(self, json_arr: Dict[str, str]):
        msg = self.vehicle_positions
        msg.Clear()

        msg.header.gtfs_realtime_version = "2.0"
        msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
        # # TODO: do better
        msg.header.timestamp = int(time.time())

        for json in json_arr:
            ent = msg.entity.add()
            self.__vehicle_json_to_pb(json, ent)
    
    def update_trip_update_feed(self, json_arr: Dict[str, str]):
        msg = self.vehicle_positions
        msg.Clear()

        msg.header.gtfs_realtime_version = "2.0"
        msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
        # # TODO: do better
        msg.header.timestamp = int(time.time())

        for json in json_arr:
            ent = msg.entity.add()
            self.__vehicle_json_to_pb(json, ent)

    def get_vehicle_positions(self) -> Union[str, None]:
        try:
            return self.vehicle_positions.SerializeToString()
        except Exception as e:
            print(e)
            return None

    def get_trip_updates() -> FeedMessage:
        pass

    def get_alerts() -> FeedMessage:
        pass

    # def get_buses(self) -> FeedMessage:
    #     return self.buses

    # def get_stops(self) -> [Dict[str, str]]:
    #     return self.stops

    # def get_routes(self) -> [Dict[str, str]]:
    #     return self.routes

    async def update(self) -> None:
        endpoint_list: List[str] = [
            endpoints.BC_BUSES,
            endpoints.BC_ROUTES,
            endpoints.BC_STOPS,
        ]

        async def fetch(url: str) -> Dict[str, str]:
            async with self.session.get(url) as response:
                return await response.json()

        json_list = await asyncio.gather(
            *[fetch(url) for url in endpoint_list], return_exceptions=True
        )

        buses_json = json_list[0]
        routes_json = json_list[1]
        stops_json = json_list[2]

        self.update_vehicle_pos_feed(buses_json)


async def test_main() -> None:
    try:
        bc_wrapper: BCTransit = BCTransit()
        await bc_wrapper.update()
        vehicle_positions: str = bc_wrapper.get_vehicle_positions()
        print(vehicle_positions)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bc_wrapper.close()


if __name__ == "__main__":
    asyncio.run(test_main())
