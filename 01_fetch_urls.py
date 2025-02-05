import os
import time
import requests

from dotenv import load_dotenv
load_dotenv()

from db import create_default_connection, get_url_200_count, get_url_not_200_count, get_one_url_to_fetch, update_url

def fetch_matrix(conn, url: str) -> None:
    token = os.getenv("MAPBOX_TOKEN")
    response = requests.get(url + "&access_token=" + token)
    status = response.status_code
    text = response.text

    update_url(conn, status, text, url)

def main():
    conn = create_default_connection()

    complete = get_url_200_count(conn)
    incomplete = get_url_not_200_count(conn)

    print(f"{complete} URLs fetched.")
    print(f"{incomplete} URLs left to process.")
    #input("[continue]")

    fetched = 0
    is_fetching = True
    while is_fetching:
        url = get_one_url_to_fetch(conn)
        print(url)
        fetched += 1
        #input(f"{fetched} of {incomplete} [continue]")
        fetch_matrix(conn, url)
        time.sleep(1)
        if fetched > 200:
            is_fetching = False

if __name__ == "__main__":
    main()
    print('exit')
