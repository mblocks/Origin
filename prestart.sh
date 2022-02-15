#! /usr/bin/env sh
mkdir -p /data/origin/origin && mkdir -p /data/origin/redis
python scripts/initial_database.py
python scripts/initial_data.py
python scripts/initial_redis.py
