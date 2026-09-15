import asyncio
import aiohttp


async def main():
    timeout = aiohttp.ClientTimeout(
        total=30,
        connect=10
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            "https://api.telegram.org"
        ) as response:

            print("STATUS:", response.status)
            print("TEXT:", await response.text())


if __name__ == "__main__":
    asyncio.run(main())