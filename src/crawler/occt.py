import aiohttp
import asyncio
import endpoints

import logging
import time


from protobufa.gtfs_realtime_pb2 import (
    FeedMessage,
    FeedHeader,
)

import google.protobuf.message as pdm

logger = logging.getLogger(__name__)


class OCCT:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.vehicle_data = {}
        self.trip_update_data = {}
        self.alert_data = {}

        pass

    def close(self) -> None:
        return self.session.close()

    async def update(self) -> None:
        endpoint_list: [str] = [
            endpoints.OCCT_VEHICLES,
            endpoints.OCCT_ROUTES,
            endpoints.OCCT_SERVICE_ANNOUNCEMENTS,
        ]

        async def fetch(url):
            async with self.session.get(url) as response:
                self.validate_res_status(response)
                return await response.json()

        json_list = await asyncio.gather(
            *[fetch(url) for url in endpoint_list], return_exceptions=True
        )

        json_list[0] = self.checkVehicles[json_list]["get_vehicles"]

        vehicles_json = json_list[0]
        routes_json = json_list[1]
        service_json = json_list[2]["get_service_announcements"]

        self.vehicle_data = self.serialize_all_vehicle_positions(vehicles_json)
        self.trip_update_data = self.serialize_all_trip_updates(vehicles_json)
        self.alert_data = self.serialize_all_alerts(vehicles_json, service_json)

        # for index, json in enumerate(json_list):
        #     setattr(self, properties[index], json)

        self.vehicle_data = self.checkVehicles(self.vehicle_data)

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
        return self.vehicle_data

    def get_stops(self):
        return self.alert_data

    def get_routes(self):
        return self.trip_update_data

    async def serialize_all_vehicle_positions(self, json_argument):
        """
        Serializes vehicle position for ONE vehicle.
        """
        msg = FeedMessage()

        # msg.header.gtfs_realtime_version = "2.0"
        msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
        # TODO: do better
        msg.header.timestamp = int(time.time())

        for vehicles_json in json_argument:
            ent = msg.entity.add()
            ent.id = "TODO"
            self.serialize_vehicle_position(ent.vehicle, vehicles_json)

        try:
            return msg.SerializeToString()
        except pbm.EncodeError as e:
            logger.error(e)
            return None

    async def serialize_vehicle_position(self, output, vehicle_json):
        output.position.latitude = vehicle_json["lat"]
        output.position.longitude = vehicle_json["lng"]
        output.stop_id = vehicle_json["nextStopID"]

    async def serialize_all_trip_updates(self, json_argument):
        """
        Serializes vehicle position for ONE vehicle.
        """
        msg = FeedMessage()

        # msg.header.gtfs_realtime_version = "2.0"
        msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
        # TODO: do better
        msg.header.timestamp = int(time.time())

        for trip_update_data in json_argument:
            ent = msg.entity.add()
            ent.id = "TODO"
            self.serialize_all_trip_update(ent.trip_update, trip_update_data)

        try:
            return msg.SerializeToString()
        except pbm.EncodeError as e:
            logger.error(e)
            return None

    async def serialize_trip_update(self, output, vehicle_json):
        output.trip.trip_id = "Bloomberg"
        output.trip.route_id = vehicle_json["routeID"]
        output.trip.start_time = vehicle_json["scheduleNumber"][2:10]
        output.stop_time_update.stop_id = vehicle_json["nextStopID"]
        output.stop_time_update.arrival.time = vehicle_json["recieveTime"] / 1000

    async def serialize_all_alerts(self, vehicle_json, alert_json):
        """
        Serializes vehicle position for ONE vehicle.
        """
        msg = FeedMessage()

        # msg.header.gtfs_realtime_version = "2.0"
        msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
        # TODO: do better
        msg.header.timestamp = int(time.time())

        for alerts_data in vehicle_json:
            ent = msg.entity.add()
            ent.id = "TODO"
            self.serialize_alert_update(ent.alert, alerts_data, alert_json)

        try:
            return msg.SerializeToString()
        except pbm.EncodeError as e:
            logger.error(e)
            return None

    async def serialize_alert_update(self, output, vehicle_json, alert_json):
        output.informed_entity.trip.trip_id = "Bloomberg"
        output.informed_entity.route_id = vehicle_json["routeID"]
        output.informed_entity.stop_id = vehicle_json["stopID"]
        output.header_text.text = "Announcement"
        output.header_text.language = "en-US"
        output.description_text.text = alert_json["announcements"]["text"]
        output.description_text.language = "en-US"


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
