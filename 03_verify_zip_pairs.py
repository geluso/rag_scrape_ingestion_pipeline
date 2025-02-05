from db import create_default_connection, get_zip_zip_distance
from wa_zip_gps import WA_ZIP_CODE_GPS

def main():
    conn = create_default_connection()
    hits = 0
    misses = 0
    total = 0
    for pick_zip, lat, longg in WA_ZIP_CODE_GPS:
        for drop_zip, lat, longg in WA_ZIP_CODE_GPS:
            total = get_zip_zip_distance(conn, pick_zip, drop_zip)
            if total == 1:
                hits += 1
            else:
                misses += 1
            total += 1
    print(hits, "hits")
    print(misses, "misses")
    print(total, "total")


if __name__ == "__main__":
    main()
    print('exit')