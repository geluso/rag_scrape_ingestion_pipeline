DROP DATABASE IF EXISTS price_sets;
DROP DATABASE IF EXISTS price_sets_test;
CREATE DATABASE price_sets;

\c price_sets;

CREATE TYPE PROCESS_STATE AS ENUM ('NONE', 'FAILED', 'SUCCESS');

CREATE TABLE urls (
  json_metadata TEXT NOT NULL,
  url TEXT NOT NULL PRIMARY KEY,
  http_status_code INTEGER DEFAULT 0,
  response TEXT DEFAULT '',
  process_state PROCESS_STATE DEFAULT 'NONE',
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zip_zip_distance (
  zip_pick VARCHAR NOT NULL,
  zip_drop VARCHAR NOT NULL,
  PRIMARY KEY (zip_pick, zip_drop),
  distance_meters INTEGER,
  distance_miles REAL
);

CREATE INDEX index_urls_url ON urls (url);

CREATE DATABASE price_sets_test WITH TEMPLATE price_sets;
