import unittest
import json
import random
from typing import List
from urllib.parse import urlparse, parse_qs

from db import create_test_connection, insert_url_row, get_url_200_count, get_url_not_200_count, update_url, \
    get_one_url_to_process, reset_db
from smc_mapbox import MapBoxResponse, ZipLatLong, ZipZipDistance, RawUrlRow


class TestResponseData(unittest.TestCase):
    def setUp(self):
        self.testdb = create_test_connection()
        reset_db(self.testdb)

        with open("test/response.data", "r") as f:
            self.text = f.read()
            self.data = json.loads(self.text)
        with open("test/json_metadata.json", "r") as f:
            self.json_metadata = f.read()
        with open("test/url.data", "r") as f:
            self.url = f.read()

    def test_json_metadata(self):
        zzds: List[ZipLatLong]  = json.loads(self.json_metadata)
        self.assertEqual(len(zzds), 24)
        zzd1 = zzds[0]
        self.assertEqual(len(zzd1), 3)
        self.assertEqual(zzd1[0], 97035)
        self.assertEqual(zzd1[1], 45.41138)
        self.assertEqual(zzd1[2], -122.72407)

    def test_parse_zips(self):
        mapbox = MapBoxResponse(self.json_metadata, self.url, self.text)
        self.assertEqual(mapbox.zips[0], 97035)
        self.assertEqual(mapbox.zips[1], 98001)
        self.assertEqual(mapbox.zips[-2], 98027)
        self.assertEqual(mapbox.zips[-1], 98028)

    def test_url(self):
        mapbox = MapBoxResponse(self.json_metadata, self.url, self.text)
        self.assertEqual(mapbox.pick_indexes, [0,1,2,3,4,5,6,7,8,9,10,11])
        self.assertEqual(mapbox.drop_indexes, [12,13,14,15,16,17,18,19,20,21,22,23])

    def test_response_code_ok(self):
        self.assertEqual(self.data["code"], "Ok")

    def test_distances_matrix_dimensions(self):
        distances = self.data["distances"]
        self.assertEqual(len(distances), 12, "Matrix should have 12 rows")
        for row in distances:
            self.assertEqual(len(row), 12, "Each row should have 12 columns")

    def test_mapbox_class(self):
        mapbox = MapBoxResponse(self.json_metadata, self.url, self.text)
        self.assertEqual(mapbox.response.code, "Ok")
        self.assertEqual(len(mapbox.response.distances), 12)
        for row in mapbox.response.distances:
            self.assertEqual(len(row), 12)

    def test_mapbox_collect_distances(self):
        mapbox = MapBoxResponse(self.json_metadata, self.url, self.text)
        distances = mapbox.collect_zip_zip_distances()
        self.assertEqual(len(distances), 144)
        self.assertEqual(distances[0].pick, 97035)
        self.assertEqual(distances[0].drop, 98013)
        self.assertEqual(distances[0].distance, 267917.6)
        self.assertEqual(distances[0].distance_miles, 167.4485)

    def test_connect_to_test_db(self):
        create_test_connection()
        self.assertTrue(True)

    def test_insert_url(self):
        insert_url_row(self.testdb, self.json_metadata, self.url + "&salt=" + str(random.random()))
        self.assertTrue(True)

    def test_url_not_200_count(self):
        count = get_url_not_200_count(self.testdb)
        insert_url_row(self.testdb, self.json_metadata, self.url + "?salt=" + str(random.random()))
        count2 = get_url_not_200_count(self.testdb)
        self.assertEqual(count2, count + 1)

    def test_url_deduped(self):
        # insert the URL once
        url = self.url + "&salt=" + str(random.random())
        insert_url_row(self.testdb, self.json_metadata, url)
        count = get_url_not_200_count(self.testdb)

        # insert the same URL over and over.
        insert_url_row(self.testdb, self.json_metadata, url)
        insert_url_row(self.testdb, self.json_metadata, url)
        insert_url_row(self.testdb, self.json_metadata, url)
        insert_url_row(self.testdb, self.json_metadata, url)
        insert_url_row(self.testdb, self.json_metadata, url)

        # make sure the number of URLs didn't change
        count2 = get_url_not_200_count(self.testdb)
        self.assertEqual(count2, count)

    def test_url_update(self):
        url = self.url + "&salt=" + str(random.random())
        insert_url_row(self.testdb, self.json_metadata, url)
        count = get_url_not_200_count(self.testdb)

        update_url(self.testdb, 200, self.text, url)
        count2 = get_url_not_200_count(self.testdb)

        self.assertEqual(count2, count - 1)

    def test_get_one_url_to_process(self):
        insert_url_row(self.testdb, self.json_metadata, self.url)
        update_url(self.testdb, 200, self.text, self.url)
        json_metadata, url, response = get_one_url_to_process(self.testdb)
        self.assertEqual(json_metadata, self.json_metadata)
        self.assertEqual(url, self.url)

    def test_parse_zips(self):
        reset_db(self.testdb)
        insert_url_row(self.testdb, self.json_metadata, self.url)
        update_url(self.testdb, 200, self.text, self.url)
        json_metadata, url, response = get_one_url_to_process(self.testdb)

        mapbox = MapBoxResponse(json_metadata, url, response)
        zips = [
            97035, 98001, 98002, 98003, 98004, 98005, 98006, 98007, 98008, 98010, 98011, 98012,
            98013, 98014, 98019, 98020, 98021, 98022, 98023, 98024, 98025, 98026, 98027, 98028
        ]
        self.assertEqual(zips, mapbox.zips)
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], mapbox.pick_indexes)
        self.assertEqual([12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], mapbox.drop_indexes)

    def test_collect_zip_zip_distances(self):
        reset_db(self.testdb)
        insert_url_row(self.testdb, self.json_metadata, self.url)
        update_url(self.testdb, 200, self.text, self.url)
        json_metadata, url, response = get_one_url_to_process(self.testdb)

        mapbox = MapBoxResponse(json_metadata, url, response)
        zzds = mapbox.collect_zip_zip_distances()
        first = zzds[0]
        last = zzds[-1]

        first_pick = 97035
        first_drop = 98013
        first_distance = 267917.6
        first_distance_miles = first_distance / 1600

        self.assertEqual(len(zzds), 144)

        self.assertEqual(first.pick, first_pick)
        self.assertEqual(first.drop, first_drop)
        self.assertEqual(first.distance, first_distance)
        self.assertEqual(first.distance_miles, first_distance_miles)
        self.assertEqual(str(first), f'{{"pick": {first_pick}, "drop": {first_drop}, "distance": {first_distance}, "distance_miles": {first_distance_miles}}}')

        last_pick = 98012
        last_drop = 98028
        last_distance = 13549.2
        last_distance_miles = last_distance / 1600

        self.assertEqual(last.pick, last_pick)
        self.assertEqual(last.drop, last_drop)
        self.assertEqual(last.distance, last_distance)
        self.assertEqual(last.distance_miles, last_distance_miles)

        for zzd in zzds:
            print(zzd)

if __name__ == '__main__':
    unittest.main()
