import json
import time
import requests
import utils
import sys


def confirm_before_sending(payload):
    """Asks the user for confirmation before sending a request."""
    print("\n" + "=" * 50)
    print("--- PENDING REQUEST CONFIRMATION ---")
    print("The script is ready to send the following data:")
    print(f"URL: {utils.API_URL}")
    print(f"Payload: {payload}")
    print("=" * 50)

    while True:
        choice = input("Proceed with sending this request? (y/n): ").lower()
        if choice == "y":
            return True
        elif choice == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def pre_sign(session, headers, config):
    print("--- Step 1: Sending pre-sign request ---")

    nonce = utils.generate_nonce()
    print(f"Generated Nonce: {nonce}")

    data_dict = {"ass_id": config["ASS_ID"], "nonce": nonce, "sign_action": "pre_sign"}
    data_json = json.dumps(data_dict)
    sign = utils.calculate_sign(data_json, config["SALT"])
    payload = f"sign={sign}&data={data_json}"

    if not confirm_before_sending(payload):
        print("Pre-sign request cancelled by user.")
        return None, None

    print("Sending pre-sign request...")
    try:
        response = session.post(utils.API_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        res_json = response.json()
        print("Pre-sign server response:", res_json)

        if res_json.get("code") == 200 and "data" in res_json:
            pre_sign_id = res_json["data"]["pre_sign_id"]
            print(f"Successfully obtained pre_sign_id: {pre_sign_id}")
            return pre_sign_id, nonce
        else:
            print("Error: Pre-sign failed -", res_json.get("msg"))
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error: Pre-sign request failed - {e}")
        return None, None


def do_sign(session, headers, config, pre_sign_id, nonce):
    print("\n--- Step 2: Starting 30-minute real-time check-in process ---")

    random_lat, random_lon = utils.randomize_coordinates(config["LATITUDE"], config["LONGITUDE"])
    points = []
    start_time = utils.get_current_timestamp_ms()
    duration_seconds = config["DURATION_SECONDS"]
    num_points = (duration_seconds // 10) + 1

    try:
        for i in range(num_points):
            point = {
                "ibeacons": [{"major": config["IBEACON_MAJOR"], "minor": config["IBEACON_MINOR"], "uuid": config["IBEACON_UUID"]}],
                "inBeacon": True,
                "latLng": {"latitude": random_lat, "longitude": random_lon, "speed": 0.0},
                "time": str(utils.get_current_timestamp_ms()),
            }
            points.append(point)

            minutes, seconds = divmod((num_points - 1 - i) * 10, 60)
            print(f"Generated point {i + 1}/{num_points}. Time remaining: ~{minutes:02d}:{seconds:02d}", end="\r")

            if i < num_points - 1:
                time.sleep(10)

        print("\nAll data points generated.")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Aborting check-in. No request will be sent.")
        sys.exit(0)

    if not points:
        print("Error: No data points were generated. Cannot check in.")
        return

    end_time = utils.get_current_timestamp_ms()
    actual_duration = (end_time - start_time) // 1000

    extra_data = {
        "ass_id": config["ASS_ID"],
        "duration": actual_duration,
        "endTime": str(end_time),
        "historyTime": end_time,
        "pauseCurSecond": 0,
        "points": points,
        "runCurSecond": actual_duration,
        "startTime": start_time,
        "userId": config["USER_ID"],
    }
    extra_json = json.dumps(extra_data, separators=(",", ":"))

    data_dict = {"ass_id": config["ASS_ID"], "extra": extra_json, "nonce": nonce, "pre_sign_id": str(pre_sign_id)}
    data_json = json.dumps(data_dict)

    sign = utils.calculate_sign(data_json, config["SALT"])
    print(f"Sending final check-in request... Sign: {sign}")
    payload = f"sign={sign}&data={data_json}"

    if not confirm_before_sending(payload):
        print("Final check-in request cancelled by user.")
        return

    try:
        response = session.post(utils.API_URL, headers=headers, data=payload, timeout=20)
        response.raise_for_status()
        res_json = response.json()
        print("\nFinal check-in server response:", res_json)

        if res_json.get("code") == 200:
            print("Check-in successful!")
        else:
            print("Error: Check-in failed -", res_json.get("msg"))

    except requests.exceptions.RequestException as e:
        print(f"Error: Final check-in request failed - {e}")
