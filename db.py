from typing import List

import psycopg2
import json

from smc_mapbox import ZipZipDistance, ZipZipDistanceRow


def create_default_connection():
    return create_connection("price_sets")

def create_test_connection():
    return create_connection("price_sets_test")

def create_connection(db_name: str):
    conn = psycopg2.connect(
        host="localhost",
        database=db_name,
        user="geluso"
    )
    return conn

def reset_db(conn):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM urls",
        )
    conn.commit()

def insert_url_row(conn, json_metadata: str, url: str):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (json_metadata, url) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (json_metadata, url)
        )
    conn.commit()

def get_urls_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM urls 
        """)
        total = cur.fetchone()[0]
        return int(total)

def get_url_200_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM urls 
            WHERE http_status_code = 200
        """)
        total = cur.fetchone()[0]
        return int(total)

def get_url_not_200_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM urls 
            WHERE http_status_code != 200
        """)
        total = cur.fetchone()[0]
        return int(total)

def get_url_processed_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM urls 
            WHERE process_state = 'SUCCESS'
        """)
        total = cur.fetchone()[0]
        return int(total)

def get_one_url_to_fetch(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT url FROM urls WHERE http_status_code = 0 LIMIT 1")
        url = cur.fetchone()[0]
        print("got", url)
        return url

def update_url(conn, status: int, text: str, url: str):
    with conn.cursor() as cur:
        cur.execute("UPDATE urls SET http_status_code = %s, response = %s WHERE url = %s", (status, text, url.strip()))
    conn.commit()

def update_url_success(conn, url):
    with conn.cursor() as cur:
        cur.execute("UPDATE urls SET process_state = %s WHERE url = %s", ('SUCCESS', url.strip()))
    conn.commit()

def get_one_url_to_process(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT json_metadata, url, response FROM urls WHERE http_status_code = 200 AND process_state = 'NONE' LIMIT 1")
        row = cur.fetchone()
        if row is None:
            return None
        json_metadata, url, response = row
        return json_metadata, url, response

def insert_zip_zip_distance(conn, zzd: ZipZipDistance):
    pick = min(zzd.pick, zzd.drop)
    drop = max(zzd.pick, zzd.drop)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO zip_zip_distance (zip_pick, zip_drop, distance_meters, distance_miles) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (pick, drop, zzd.distance, zzd.distance_miles)
        )
    conn.commit()

def count_zip_zip_distance(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM zip_zip_distance
        """)
        total = cur.fetchone()[0]
        return int(total)

def get_zip_zip_distance(conn, zip_pick, zip_drop):
    with conn.cursor() as cur:
        cur.execute("""SELECT COUNT(*) FROM zip_zip_distance WHERE zip_pick = %s AND zip_drop = %s""", (str(zip_pick), str(zip_drop)))
        total = cur.fetchone()[0]
        return int(total)

def get_zip_zip_distance_distance(conn, zip_pick, zip_drop):
    if zip_pick == zip_drop:
        return 0
    with conn.cursor() as cur:
        cur.execute("""SELECT distance_miles FROM zip_zip_distance WHERE zip_pick = %s AND zip_drop = %s OR zip_pick = %s AND zip_drop = %s""", (str(zip_pick), str(zip_drop), str(zip_drop), str(zip_pick)))
        try:
            distance = cur.fetchone()[0]
            return float(distance)
        except Exception as e:
            return -1

def get_all_zip_zip_distances(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT zip_pick, zip_drop, distance_meters FROM zip_zip_distance""")
        all: List[ZipZipDistanceRow] = cur.fetchall()
        return [ZipZipDistance(*item) for item in all]
