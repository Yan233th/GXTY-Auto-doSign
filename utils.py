import time
import uuid
import hashlib
import random

API_URL = "http://www.sportcampus.cn/api/association/doSign"


def get_current_timestamp_ms():
    return int(time.time() * 1000)


def generate_nonce():
    return uuid.uuid4().hex


def calculate_sign(data_json_str, salt):
    string_to_sign = salt + "data" + data_json_str
    return hashlib.md5(string_to_sign.encode("utf-8")).hexdigest()


def randomize_coordinates(lat, lon):
    new_lat = lat + random.uniform(0.000005, 0.00005)
    new_lon = lon + random.uniform(0.000005, 0.00005)
    print(f"Coordinates randomized to: ({new_lat:.6f}, {new_lon:.6f})")
    return new_lat, new_lon
