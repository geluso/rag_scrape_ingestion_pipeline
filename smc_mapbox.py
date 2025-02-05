import json
from typing import List, Tuple
from urllib.parse import urlparse, parse_qs

ZipLatLong = Tuple[int, float, float]
RawUrlRow = Tuple[str, str, int, str]
ZipZipDistanceRow = Tuple[str, str, int, float]
MapBoxDistanceMatrix = List[List[int]]
JsonMetadata = List[ZipLatLong]

class ZipZipDistance:
  def __init__(self, pick: int, drop: int, distance: float):
    self.pick = pick
    self.drop = drop
    self.distance = distance
    self.distance_miles = distance / 1600

  def __str__(self):
    return f'{{"pick": {self.pick}, "drop": {self.drop}, "distance": {self.distance}, "distance_miles": {self.distance_miles}}}'

class UrlRow:
  def __init__(self, row: RawUrlRow):
      self.json_metadata: str = row[0]
      self.url: str = row[1]
      self.http_status_code: int = row[2]
      self.response: str = row[3]

class Response:
  code: str
  distances: MapBoxDistanceMatrix

  def __init__(self, code: str, distances: MapBoxDistanceMatrix):
    self.code = code
    self.distances = distances

class MapBoxResponse:
  url: str
  json_metadata: JsonMetadata
  response: Response

  zips: List[int]
  pick_indexes: List[int]
  drop_indexes: List[int]
  distances: List[ZipZipDistance]

  def __init__(self, json_metadata, url, response):
    self.json_metadata = self.parse_raw_json_metadata(json_metadata)
    self.url = url
    self.response = self.parse_raw_response(response)

    self.zips = self.parse_zips()
    self.pick_indexes, self.drop_indexes = self.parse_url()
    self.distances = self.collect_zip_zip_distances()


  def parse_raw_json_metadata(self, raw_json_metadata: str) -> JsonMetadata:
    return json.loads(raw_json_metadata)

  def parse_raw_response(self, raw_response: str):
    jj = json.loads(raw_response)
    if "code" not in jj:
      self.error = True
      return
    if "distances" not in jj:
      self.error = True
      return

    code: str = jj["code"]
    distances: MapBoxDistanceMatrix = jj["distances"]
    return Response(code, distances)

  def parse_zips(self):
    return list(map(lambda zll: zll[0], self.json_metadata))

  def index_to_zip(self, index):
    return self.json_metadata[int(index)][0]

  def parse_url(self):
    parsed_url = urlparse(self.url)
    query_params = parse_qs(parsed_url.query)
    pick_indexes = list(map(int, query_params['sources'][0].split(';')))
    drop_indexes = list(map(int, query_params['destinations'][0].split(';')))
    return pick_indexes, drop_indexes

  def collect_zip_zip_distances(self) -> List[ZipZipDistance]:
    zip_zip_distances: List[ZipZipDistance] = []
    for (rowi, pick_row) in enumerate(self.response.distances):
      for (coli, distance) in enumerate(pick_row):
        zip_pick = self.zips[self.pick_indexes[rowi]]
        zip_drop = self.zips[self.drop_indexes[coli]]
        zzd = ZipZipDistance(zip_pick, zip_drop, distance)
        zip_zip_distances.append(zzd)
    return zip_zip_distances

    