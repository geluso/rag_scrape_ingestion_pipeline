import json
import time
import psycopg2
import requests
from typing import List, Tuple
from document_payload import DocumentPayload
import html2text


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
        metadata, url, response = row

        ngrok_url = "https://4cb3-2601-602-8b82-92b0-64d0-4b7b-a51a-85fb.ngrok-free.app"
        base_url = ngrok_url
        url_add_document = base_url + "/add_document/"

        text = html2text.html2text(response)
        print("html2text", len(text), text)

        doc = DocumentPayload(url, url, text)
        response = requests.post(url_add_document, json=doc.to_dict())
        print(response.text)

        update_url_success(conn, url)

if __name__ == "__main__":
    main()
    print('exit')