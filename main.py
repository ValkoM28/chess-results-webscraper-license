"""
    This script checks all the database keys it gets in the keys.txt file, returns the tournament name and the 
    swiss-manager license of the tournament arbiter. 
    It was made just for the purpose of checking unauthorized license usage through the slovak chess federation. 
    The code quality correlates with its single-use purpose. 
"""
import aiohttp
import asyncio
import html
import requests
from typing import Iterator, Tuple


class UrlSet:     
    def __init__(self, database_keys:list): 
        self.keys = database_keys

    def get_next_url(self): 
        return "https://chess-results.com/tnr" + self.keys.pop().strip() + ".aspx" if len(self.keys) >= 1 else -1


async def fetch_page(session:aiohttp.ClientSession, url:str) -> str: 
    """Asynchronous fetch to get the HTML page."""
    async with session.get(url) as response:
        return await response.text()


async def process_url(session: aiohttp.ClientSession, url: str) -> Tuple[str, str, str]: 
    raw_page = await fetch_page(session, url)
    index_tournament: int = raw_page.find("h2")
    index_license: int = raw_page.find("Creator/Last")

    tournament_string:str = raw_page[index_tournament:index_tournament+55:]
    temp:int = tournament_string.find("<")
    tournament_string:str = tournament_string[3:temp:]

    license_string:str = raw_page[index_license:index_license+55:]
    temp:int = license_string.find("<")
    license_string:str = license_string[:temp:]

    tournament_string = html.unescape(tournament_string)
    license_string = html.unescape(license_string)
    print(f"Processed {url} successfully.")

    return tournament_string, url, license_string


async def main(database_keys:UrlSet):
    async with aiohttp.ClientSession() as session:
        tasks: list = []
        while ((url := database_keys.get_next_url()) != -1): 
            tasks.append(process_url(session, url))
        
        results = await asyncio.gather(*tasks)

        output_formatted = "".join([f"{result[0]}\n{result[1]}\n{result[2]}\n\n" for result in results])

        with open("out.txt", "w", encoding="UTF-8") as file:
            file.write(output_formatted)


if __name__ == "__main__": 
    with open("keys.txt") as file: 
        keys = file.readlines()
    urls = UrlSet(keys)
    asyncio.run(main(urls))
