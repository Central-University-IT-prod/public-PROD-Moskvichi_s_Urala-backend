#!/bin/bash
set -e
ps -ef | grep postgres
psql -v ON_ERROR_STOP=1 --username db_user --dbname db_name <<-EOSQL
  INSERT INTO (name, life_time, ref_url) VALUES ("2-НДФЛ", 6060, "google.com")

EOSQL