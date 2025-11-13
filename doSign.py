import os
import sys
import requests
from dotenv import load_dotenv
import api


def load_config():
    load_dotenv()

    config = {}
    required_vars = [
        "USER_ID",
        "UTOKEN",
        "SALT",
        "ASS_ID",
        "DURATION_SECONDS",
        "LATITUDE",
        "LONGITUDE",
        "IBEACON_UUID",
        "IBEACON_MAJOR",
        "IBEACON_MINOR",
        "USER_AGENT",
        "X_CHANNEL",
        "PACKAGENAME",
        "XXVERSIONXX",
        "VERSIONNAME",
        "VERSIONCODE",
        "PLATFORM",
        "DRID",
        "E20_HEADER",
        "UUID_HEADER",
    ]

    if not all(os.getenv(var) for var in required_vars):
        print("Error: Missing required configuration in .env file. Please check.")
        sys.exit(1)

    for var in required_vars:
        config[var] = os.getenv(var)

    try:
        config["DURATION_SECONDS"] = int(config["DURATION_SECONDS"])
        config["LATITUDE"] = float(config["LATITUDE"])
        config["LONGITUDE"] = float(config["LONGITUDE"])
    except ValueError:
        print("Error: DURATION_SECONDS, LATITUDE, or LONGITUDE in .env are not valid numbers.")
        sys.exit(1)

    return config


def run_check_in_process():
    print("--- Starting check-in process ---")
    config = load_config()
    print("Configuration loaded successfully!")

    headers = {
        "User-Agent": config["USER_AGENT"],
        "X-Channel": config["X_CHANNEL"],
        "packagename": config["PACKAGENAME"],
        "xxversionxx": config["XXVERSIONXX"],
        "versionName": config["VERSIONNAME"],
        "versionCode": config["VERSIONCODE"],
        "platform": config["PLATFORM"],
        "drid": config["DRID"],
        "E206B53E98E9ECC295427AA5E1A4C18B": config["E20_HEADER"],
        "uuid": config["UUID_HEADER"],
        "utoken": config["UTOKEN"],
        "Host": "www.sportcampus.cn",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-form-urlencoded",
    }

    with requests.Session() as session:
        pre_sign_id, nonce = api.pre_sign(session, headers, config)

        if pre_sign_id and nonce:
            api.do_sign(session, headers, config, pre_sign_id, nonce)
        else:
            print("\nProcess terminated due to pre-sign failure. Please check UTOKEN in .env and network connection.")


if __name__ == "__main__":
    run_check_in_process()
