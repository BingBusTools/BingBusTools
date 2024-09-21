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
        futs = [stops(session), trips(session), stop_times(session)]
    futs = [asyncio.create_task(f) for f in futs]
    # asyncio.gather(*futs)
    for f in futs:
        await f


async def stops(session: aiohttp.ClientSession):
    data = None
    async with session.get(stops_url) as response:
        data = (await response.json())["get_stops"]
    with open("stops.txt", "w+") as file:
        print("stop_id,stop_name,stop_lat,stop_lon", file=file)
        for stop in data:
            print(
                f"{stop["id"]},{stop["name"]},{stop["lat"]},{stop["lng"]}",
                file=file,
            )


async def trips(session: aiohttp.ClientSession):
    stops_data = None
    routes_data = None
    async with session.get(stops_url) as response:
        stops_data = (await response.json())["get_stops"]
    async with session.get(routes_url) as response:
        routes_data = (await response.json())["get_routes"]
    async with session.get(html_path) as response:
        pass


async def stop_times(session: aiohttp.ClientSession):
    async with aiohttp.ClientSession() as session:
        for html_path in html_grabs:
            soup = None
            async with session.get(html_path) as response:
                soup = BeautifulSoup(await response.text(), features="html.parser")
            elem = soup.select_one(".container-title")
            assert elem is not None
            elem = elem.select_one("span")
            assert elem is not None
            title = elem.string
            print(f"title: {title}")


asyncio.run(main())
