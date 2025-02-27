import json
from typing import List, Tuple

from db import create_default_connection, insert_url_row

def main():
    conn = create_default_connection()
    with open("./urls/south_carolina", "r") as f:
        for line in f:
            url = line.strip()
            print("inserting", url)
            insert_url_row(conn, json.dumps({}), url)

if __name__ == "__main__":
    main()
    print('exit')
