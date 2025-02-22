"""
    This script checks all the database keys it gets in the keys.txt file, returns the tournament name and the 
    swiss-manager license of the tournament arbiter. 
    It was made just for the purpose of checking unauthorized license usage through the slovak chess federation. 
    The code quality correlates with its single-use purpose. 
"""

import requests
import html
from typing import Iterator, Tuple


class UrlSet:     
    def __init__(self, database_keys:list): 
        self.keys = database_keys

    def get_next_url(self): 
        return "https://chess-results.com/tnr" + self.keys.pop().strip() + ".aspx" if len(self.keys) >= 1 else -1


def main(database_keys:UrlSet) -> Iterator[Tuple[str, str]]:
    url = database_keys.get_next_url()

    while (url != -1): 
        raw_page = requests.get(url)

        page_html:str = raw_page.text
        index_tournament:int = page_html.find("h2")
        index_license:int = page_html.find("Creator/Last")

        tournament_string:str = page_html[index_tournament:index_tournament+55:]
        temp:int = tournament_string.find("<")
        tournament_string:str = tournament_string[3:temp:]

        license_string:str = page_html[index_license:index_license+55:]
        temp:int = license_string.find("<")
        license_string:str = license_string[:temp:]

        temp:str = url
        print(f"{url} examined successfully!")

        url:str = database_keys.get_next_url()

        yield html.unescape(tournament_string), temp, license_string



if __name__ == "__main__": 
    with open("keys.txt") as file: 
        keys = file.readlines()

    urls:UrlSet = UrlSet(keys)

    output = list(main(urls))

    output_formated = "".join([i[0] + "\n" + i[1] + "\n" + i[2] + "\n\n" for i in output])

    with open("out.txt", "w", encoding="UTF-8") as file: 
        file.write(output_formated)
