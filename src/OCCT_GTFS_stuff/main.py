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


async def main():
    futs = [stop_times()]
    await concurrent.futures.wait(futs)


async def stop_times():
    async with aiohttp.ClientSession() as session:
        for html_path in html_grabs:
            soup = None
            async with session.get(html_path) as response:
                soup = BeautifulSoup(await response.text())
            elem = soup.select_one(".container-title")
            assert elem is not None
            elem = elem.select_one("span")
            assert elem is not None
            title = elem.string
            print(f"title: {title}")


asyncio.run(main())
