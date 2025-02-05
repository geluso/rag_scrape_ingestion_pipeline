import json
import time
import psycopg2
import requests
from typing import List, Tuple

from db import create_default_connection, get_url_200_count, get_urls_count, \
    get_one_url_to_process, insert_zip_zip_distance, count_zip_zip_distance, get_url_processed_count, \
    update_url_success
from smc_mapbox import MapBoxResponse


def main():
    conn = create_default_connection()
    fetched = get_url_200_count(conn)
    processed = get_url_processed_count(conn)
    total = get_urls_count(conn)
    print(f"{fetched} fetched")
    print(f"{processed} processed")
    print(f"{total} total URLs")

    is_processing = True
    while is_processing:
        row = get_one_url_to_process(conn)
        if row is None:
            is_processing = False
            continue
        json_metadata, url, response = row
        mapbox = MapBoxResponse(json_metadata, url, response)
        zzds = mapbox.collect_zip_zip_distances()

        for zzd in zzds:
            print(zzd)
            insert_zip_zip_distance(conn, zzd)

        update_url_success(conn, url)

        total_zzds = count_zip_zip_distance(conn)
        print(f"{total_zzds} distances")
        #input("[continue]")

if __name__ == "__main__":
    main()
    print('exit')