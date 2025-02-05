import json
from typing import List, Tuple

from db import create_default_connection, insert_url_row
from wa_zip_gps import WA_ZIP_CODE_GPS

def make_batch(size: int, picki: int, dropi: int) -> List[Tuple[int, float, float]]:
    picks = WA_ZIP_CODE_GPS[picki:picki + size]
    drops = WA_ZIP_CODE_GPS[dropi:dropi + size] 
    batch = picks + drops
    return batch

def format_url(batch: List[Tuple[int, float, float]]) -> Tuple[List[Tuple[int, float, float]], str]:
    sources = ";".join(str(i) for i in range(12))
    destinations = ";".join(str(i) for i in range(12, 24))
    locations = ";".join(f"{lng},{lat}" for _, lat, lng in batch)
    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{locations}?sources={sources}&annotations=distance&destinations={destinations}"
    print(url)
    return batch, url

def main():
    urls = []
    size = 12

    for pick in range(0, len(WA_ZIP_CODE_GPS), size):
        for drop in range(0, len(WA_ZIP_CODE_GPS), size):
            if drop > pick:
                batch = make_batch(size, pick, drop)
                batch_url_pair = format_url(batch)
                urls.append(batch_url_pair)

    conn = create_default_connection()
    for url in urls:
        print("inserting", url)
        insert_url_row(conn, json.dumps(url[0]), url[1])

if __name__ == "__main__":
    main()
    print('exit')