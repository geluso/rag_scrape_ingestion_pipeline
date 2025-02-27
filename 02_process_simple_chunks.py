import json
import time
import psycopg2
import requests
from typing import List, Tuple
from document_payload import DocumentPayload
import html2text


from db import create_default_connection, get_url_200_count, get_urls_count, \
    get_one_url_to_process, insert_zip_zip_distance, count_zip_zip_distance, get_url_processed_count, \
    update_url_success, get_all_urls
from smc_mapbox import MapBoxResponse

def text_to_chunks(text):
    words = text.split()
    chunks = []
    while len(words) > 0:
        chunk = " ".join(words[:350])
        words = words[350:]
        chunks.append(chunk)
    return chunks

def main():
    conn = create_default_connection()
    fetched = get_url_200_count(conn)
    processed = get_url_processed_count(conn)
    total = get_urls_count(conn)
    print(f"{fetched} fetched")
    print(f"{processed} processed")
    print(f"{total} total URLs")

    url_sizes = []

    for row in get_all_urls(conn):
        if row is None:
            is_processing = False
            continue
        metadata, url, response = row

        ngrok_url = "https://4cb3-2601-602-8b82-92b0-64d0-4b7b-a51a-85fb.ngrok-free.app"
        base_url = ngrok_url
        url_add_document = base_url + "/add_document/"

        text = html2text.html2text(response)
        if "scstatehouse" not in url:
            print("skipping", url)
            continue

        chunks = text_to_chunks(text)
        url_sizes.append(len(chunks))
        for chunk in chunks:
            doc = DocumentPayload(url, url, chunk)
            response = requests.post(url_add_document, json=doc.to_dict())
            time.sleep(1)
            print(url, response.text)
    url_sizes.sort()
    print(url_sizes)

if __name__ == "__main__":
    main()
    print('exit')