import csv
from datetime import datetime

from db import create_default_connection, get_zip_zip_distance, get_all_zip_zip_distances, get_zip_zip_distance_distance
from wa_zip_gps import WA_ZIP_CODE_GPS
from zip_codes import zone_to_zips


def main():
    conn = create_default_connection()
    all = get_all_zip_zip_distances(conn)

    sheet = []
    with open('./csv/2024_01_17.csv', newline='') as csvfile:
        price_sets = csv.reader(csvfile)
        for row in price_sets:
            sheet.append(row)

    new_sheet = []
    new_sheet.append(list(sheet[0]))

    hits = 0
    misses = 0
    total = 0

    rowi = 1
    while rowi < len(sheet):
        new_row = [''] * len(sheet[rowi])
        new_row[0] = sheet[rowi][0]

        coli = 1
        while coli < len(new_row):
            zone_pick = sheet[rowi][0]
            zone_drop = sheet[0][coli]

            zips_pick = zone_to_zips[zone_pick]
            zips_drop = zone_to_zips[zone_drop]

            total += 1
            if rowi == coli:
                new_row[coli] = 0
                hits += 1
            else:
                distances = []
                distance_total = 0
                for zip_pick in zips_pick:
                    for zip_drop in zips_drop:
                        distance1 = get_zip_zip_distance_distance(conn, zip_pick, zip_drop)
                        distance2 = get_zip_zip_distance_distance(conn, zip_drop, zip_pick)
                        breakpoint()
                        if distance1 > 0:
                            distances.append(distance1)
                            distance_total += distance1
                        if distance2 > 0:
                            distances.append(distance2)
                            distance_total += distance2

                if len(distances) > 0:
                    min_distance = min(distances)
                    max_distance = max(distances)
                    diff = abs(min_distance - max_distance)
                    ave_distance = distance_total / len(distances)
                    #if diff > 0:
                    #    print(diff, min_distance, max_distance, ave_distance, zone_pick, zone_drop)
                    new_row[coli] = ave_distance
                    hits += 1
                else:
                    misses += 1
            coli += 1
        rowi += 1
        new_sheet.append(new_row)

    print(misses, "misses")
    print(str(hits / total * 100) + "% complete")
    now = datetime.now()
    filename = f'./csv/{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}.csv'
    with open(filename, 'w', newline='') as csvfile:
        new_csv = csv.writer(csvfile)
        for row in new_sheet:
            new_csv.writerow(row)

if __name__ == "__main__":
    main()
    print('exit')