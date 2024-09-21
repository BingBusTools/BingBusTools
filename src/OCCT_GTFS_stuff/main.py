from io import TextIOWrapper
import re
from bs4 import BeautifulSoup
import bs4
import aiohttp
import asyncio


html_grabs = [
    "https://occtransport.org/pages/routes/ws-out.html",
    "https://occtransport.org/pages/routes/ws-in.html",
    "https://occtransport.org/pages/routes/ms-out.html",
    "https://occtransport.org/pages/routes/ms-in.html",
    "https://occtransport.org/pages/routes/dcl-out.html",
    "https://occtransport.org/pages/routes/dcl-in.html",
    "https://occtransport.org/pages/routes/udc-out.html",
    "https://occtransport.org/pages/routes/udc-in.html",
    "https://occtransport.org/pages/routes/ds-out.html",
    # uses text ewww
    # "https://occtransport.org/pages/routes/cs.html",
    "https://occtransport.org/pages/routes/uc.html",
    # doesn't exist in API I think
    # "https://occtransport.org/pages/routes/iu.html",
]

routes_url = (
    "https://binghamtonupublic.etaspot.net/service.php?service=get_routes&token=TESTING"
)
stops_url = (
    "https://binghamtonupublic.etaspot.net/service.php?service=get_stops&token=TESTING"
)


async def main():
    async with aiohttp.ClientSession() as session:
        futs = [stops(session), routes(session), trips(session)]
        futs = [asyncio.create_task(f) for f in futs]
        for f in futs:
            await f


async def stops(session: aiohttp.ClientSession):
    data = None
    async with session.get(stops_url) as response:
        data = (await response.json())["get_stops"]
    with open("stops.txt", "w+") as file:
        print("stop_id,stop_name,stop_lat,stop_lon", file=file)
        for stop in data:
            print(f"{stop["id"]},{stop["name"]},{stop["lat"]},{stop["lng"]}", file=file)


async def calendar(session: aiohttp.ClientSession):
    with open("calendar.txt", "w+") as file:
        print(
            "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date",
            file=file,
        )
        print("wd,1,1,1,1,1,0,0", file=file)
        print("we,0,0,0,0,0,1,1", file=file)


class Trip:
    route: str
    start_time: str
    end_time: str
    calendar: str
    start_stop: str
    end_stop: str

    def __init__(
        self,
        route: str,
        start_time: str,
        end_time: str,
        calendar: str,
        start_stop: str,
        end_stop: str,
    ):
        start_match = re.match(r"[0-9]{1,2}:[0-9]{2}\s*[AP]M", start_time)
        end_match = re.match(r"[0-9]{1,2}:[0-9]{2}\s*[AP]M", end_time)

        assert start_match is not None
        assert end_match is not None

        self.route = route

        self.start_time = start_time[start_match.pos : start_match.endpos]
        self.end_time = end_time[end_match.pos : end_match.endpos]
        self.calendar = calendar
        self.start_stop = start_stop
        self.end_stop = end_stop


async def trips(session: aiohttp.ClientSession):
    # maps route-(we/wd) to a list of tuples with start and end times
    trips = []
    data = None
    async with session.get(routes_url) as response:
        data = (await response.json())["get_routes"]
    assert isinstance(data, list)
    for html_yoink in html_grabs:
        async with session.get(html_yoink) as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, features="html.parser")

            route_name = soup.select_one(".container-title")
            assert route_name is not None

            route_name = route_name.get_text()
            route_name = route_name.replace("-", " ")
            route_name = route_name.replace("St ", "")
            route_name = route_name.replace(" Shuttle", "")
            route_name = route_name.strip()
            if route_name.upper() == "UCLUB":
                route_name = "UCLUB"
            print(route_name)
            content_box = soup.select_one(".content_box")
            assert content_box is not None
            weekdays = content_box.findChildren("div")[0]
            weekends = content_box.findChildren("div")[2]

            weekdays = weekdays.findChildren("table")[0]
            weekends = weekends.findChildren("table")[0]

            # weekdays = weekdays.select_one("table")

            assert weekdays is not None
            assert weekends is not None

            weekdays = weekdays.select_one("tbody")
            weekends = weekends.select_one("tbody")
            assert weekdays is not None
            assert weekends is not None

            for row in weekdays.select("tr"):
                columns = row.select("td")
                start = columns[0]
                end = columns[-1]
                real_route = None
                for route in data:
                    route["name"] = route["name"].replace("-", " ")
                    route["name"] = route["name"].strip()
                    if route["name"] == route_name:
                        real_route = route
                        break

                assert real_route is not None
                assert real_route["id"] is not None
                assert real_route["stops"] is not None

                trips.append(
                    Trip(
                        real_route["id"],
                        start.get_text(),
                        end.get_text(),
                        "wd",
                        real_route["stops"][0],
                        real_route["stops"][-1],
                    )
                )
            for row in weekends.select("tr"):
                columns = row.select("td")
                start = columns[0]
                end = columns[-1]
                real_route = None
                for route in data:
                    route["name"].replace("-", " ")
                    if route["name"] == route_name:
                        real_route = route
                        break
                assert real_route is not None
                assert real_route["id"] is not None
                assert real_route["stops"] is not None

                trips.append(
                    Trip(
                        real_route["id"],
                        start.get_text(),
                        end.get_text(),
                        "we",
                        real_route["stops"][0],
                        real_route["stops"][-1],
                    )
                )

    with open("trips.txt", "w+") as trip:
        with open("stop_times.txt", "w+") as stop_times:
            await process_trips(trip, stop_times, trips)


async def process_trips(
    trip_file: TextIOWrapper, stop_times_file: TextIOWrapper, trips: list[Trip]
):
    print("route_id,service_id,trip_id", file=trip_file)
    print(
        "trip_id,arrival_time,departure_time,stop_sequence,timepoint,stop_id",
        file=stop_times_file,
    )
    for trip in trips:
        trip_id = f"{trip.route}-{trip.start_time}-{trip.calendar}"
        print(f"{trip.route},{trip.calendar},{trip_id}", file=trip_file)
        print(
            f"{trip_id},{trip.start_time},{trip.start_time},0,0,{trip.start_stop}",
            file=stop_times_file,
        )
        # if OCCT has more than 255 stops for a trip I will be surprised
        print(
            f"{trip_id},{trip.end_time},{trip.end_time},255,0,{trip.end_stop}",
            file=stop_times_file,
        )


# optional
async def shapes(session: aiohttp.ClientSession):
    pass


async def routes(session: aiohttp.ClientSession):
    data = None
    async with session.get(routes_url) as response:
        data = (await response.json())["get_routes"]
    with open("routes.txt", "w+") as file:
        print(
            "route_id,agency_id,route_short_name,route_long_name,route_type,route_color",
            file=file,
        )
        for route in data:
            print(
                f"{route["id"]},{0},{route["abbr"]},{route["name"]},{3},{route["color"]}",
                file=file,
            )


async def agency(session: aiohttp.ClientSession):
    with open("agency.txt", "w+") as file:
        print(
            "agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone",
            file=file,
        )
        print(
            "0,OCCT,https://occtransport.org/index.html,America/New_York,en,1-607-777-6989",
            file=file,
        )


if __name__ == "__main__":
    asyncio.run(main())
