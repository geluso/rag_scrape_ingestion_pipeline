import csv
import sys

from zip_codes import zone_to_zips 

def main():
    with open(sys.argv[1], newline='') as csvfile:
        sheet = list(csv.reader(csvfile))

        hits = 0
        misses = 0
        sames = 0
        total = 0

        rowi = 1
        while rowi < len(sheet):
            coli = 1
            while coli < len(sheet[rowi]):
                zone_pick = sheet[rowi][0]
                zone_drop = sheet[0][coli]
                distance = sheet[rowi][coli]
                total += 1
                if rowi == coli:
                    sames += 1
                elif distance:
                    hits += 1
                else:
                    misses += 1
                    print("pick", zone_pick, zone_to_zips[zone_pick])
                    print("drop", zone_drop, zone_to_zips[zone_drop])
                    print()
                coli += 1
            rowi += 1

        print(hits, "hits")
        print(misses, "misses")
        print(sames, "sames")
        print(total, "total")

if __name__ == "__main__":
    main()
    print('exit')