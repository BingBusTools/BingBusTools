from bs4 import BeautifulSoup
import concurrent.futures
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
    "https://occtransport.org/pages/routes/cs.html",
    "https://occtransport.org/pages/routes/uc.html",
    "https://occtransport.org/pages/routes/iu.html",
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
        print(f"0,1,1,1,1,1,1,1")


async def trips(session: aiohttp.ClientSession):
    routes_data = None
    route_times = {}
    for html_path in html_grabs:
        soup = None
        async with session.get(html_path) as response:
            soup = BeautifulSoup(await response.text(), features="html.parser")
        elem = soup.select_one(".container-title")
        assert elem is not None
        elem = elem.select_one("span")
        assert elem is not None
        title = elem.string
        assert title is not None
        title.replace("-"," ")
        route_times[title] = {}
        box = soup.select_one("content_box")
        assert box is not None
        assert box.contents[0] is not None
        assert box.contents[1] is not None
        box.contents
        route_times[title]["wd"] = box.
        route_times[title]["we"] = box.contents[1]
    async with session.get(routes_url) as response:
        routes_data = (await response.json())["get_routes"]
    with open("trips.txt", "w+") as trips:
        with open("stop_times.txt", "w+") as stop_times:
            print("route_id,service_id,trip_id,bikes_allowed", file=trips)
            for i, route in enumerate(routes_data):
                for t in ["wd","we"]:
                    for time in []
                        print(f"{route["id"]},{0},{f"{route["id"]}-"},1", file=stop_times)


# optional
async def shapes(session: aiohttp.ClientSession):
    pass


async def stop_times(session: aiohttp.ClientSession):
    async with aiohttp.ClientSession() as session:


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
        print("agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone", file=file)
        print(
            "0,OCCT,https://occtransport.org/index.html,America/New_York,en,1-607-777-6989", file=file
        )


if __name__ == "__main__":
    asyncio.run(main())
