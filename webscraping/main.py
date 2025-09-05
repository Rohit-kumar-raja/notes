import httpx
import asyncio


async def getDatafromInternet(url: str):
    async with httpx.AsyncClient() as client:
       print(url)
       await client.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
            },
        )


for x in range(1, 500):
    url = f"https://www.naukri.com/jobs-in-gurgaon-{x}"
    asyncio.run(getDatafromInternet(url))
    # getDatafromInternet(url)
