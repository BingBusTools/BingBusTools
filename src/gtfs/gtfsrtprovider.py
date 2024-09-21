import logging
import time
from protobuf.gtfs_realtime_pb2 import FeedMessage, FeedHeader
import google.protobuf.message as pbm

logger = logging.getLogger(__name__)


async def get_vehicle_position():
    """
    Serializes vehicle position for ONE vehicle.
    """
    msg = FeedMessage()

    # msg.header.gtfs_realtime_version = "2.0"
    msg.header.incrementality = FeedHeader.Incrementality.FULL_DATASET
    # TODO: do better
    msg.header.timestamp = int(time.time())

    ent = msg.entity.add()
    ent.id = "TODO"

    ent.vehicle.position.latitude = 42.10383
    ent.vehicle.position.longitude = -75.93134

    try:
        return msg.SerializeToString()
    except pbm.EncodeError as e:
        logger.error(e)
        return None


async def main():
    print("Hello from gtfs-rt!")
    await get_vehicle_position()
