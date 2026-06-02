import os
import json
import threading
import time
import pytest


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def get_dataentry_scenarios():
    """Reads the scenarios from the external JSON file."""
    current_dir = os.path.dirname(__file__)
    scenarios_path = os.path.join(current_dir, '..', 'test_data', 'dataentry_scenarios.json')
    with open(scenarios_path, 'r') as file:
        return json.load(file)


def take_failure_screenshot(test_name):
    """Takes an ADB screenshot and saves it to the local reports folder."""
    os.makedirs('reports', exist_ok=True)
    filename = f"FAIL_{test_name}.png"
    print(f"\n[EVIDENCE] Capturing screenshot of failure: {filename}...")

    os.system(f"adb shell screencap -p /sdcard/{filename}")
    os.system(f"adb pull /sdcard/{filename} reports/{filename}")
    os.system(f"adb shell rm /sdcard/{filename}")
    print(f"   -> Screenshot saved locally at: reports/{filename}")


scenarios = get_dataentry_scenarios()


# =========================================================================
# THE TEST ENGINE
# =========================================================================

@pytest.mark.parametrize("scenario", scenarios, ids=[s["test_name"] for s in scenarios])
def test_dynamic_dataentry(ws_client, adb_manager, scenario):
    test_name = scenario["test_name"]
    datatype = scenario["datatype"]
    input_to_tap = scenario["input_to_tap"]
    expected_response = scenario["expected_response"]
    test_title = scenario.get("title", "Please enter data")

    print(f"\n{'=' * 65}")
    print(f"[START] Executing Test Case: {test_name}")
    print(f"   -> Target Datatype: '{datatype}'")
    print(f"   -> Expecting Response: '{expected_response}'")
    print(f"{'=' * 65}")

    # --- STEP 1: UI INTERACTION ---
    print(f"[STEP 1] Spawning background ADB thread to tap sequence: '{input_to_tap}'...")
    ui_thread = threading.Thread(
        target=adb_manager.enter_pinpad_data,
        args=(input_to_tap, "344", "825")
    )
    ui_thread.start()

    # --- STEP 2: LOAD & MUTATE JSON ---
    print(f"[STEP 2] Loading JSON template and injecting dynamic data...")
    current_dir = os.path.dirname(__file__)
    payload_path = os.path.join(current_dir, '..', 'test_data', 'dataentry.json')
    with open(payload_path, 'r') as file:
        dynamic_payload = json.load(file)

    dynamic_payload["request"]["datatype"] = datatype
    dynamic_payload["request"]["title"] = test_title

    # =========================================================================
    # EXECUTION & VALIDATION
    # =========================================================================
    try:
        # --- STEP 3: TRANSMIT PAYLOAD ---
        print(f"[STEP 3] Transmitting payload to EloPayLink via WebSocket...")
        actual_response = ws_client.send_dict_payload(dynamic_payload)

        # --- STEP 4: ASSERTIONS ---
        print(f"[STEP 4] Validating WebSocket Response...")

        if actual_response is None:
            raise Exception("Expected a WebSocket response, but got a timeout!")

        if "response" not in actual_response:
            raise Exception(f"Expected 'response' block, got: {actual_response}")

        resp_data = actual_response["response"]

        if resp_data.get("command") != "dataentry":
            raise Exception(f"Command mismatch. Expected 'dataentry', got '{resp_data.get('command')}'")
        print(f"   [OK] Command verified: 'dataentry'")

        if resp_data.get("responseCode") != "00000":
            raise Exception(f"Status code mismatch. Expected '00000', got '{resp_data.get('responseCode')}'")
        print(f"   [OK] Status code verified: '00000' (Success)")

        captured_data = resp_data.get("enteredValue")
        if captured_data != expected_response:
            raise Exception(f"Data mismatch. Expected '{expected_response}', got '{captured_data}'")
        print(f"   [OK] Data format verified! Device correctly processed input as: '{captured_data}'")

        print(f"\n[SUCCESS] Test '{test_name}' executed perfectly.")

    # =========================================================================
    # FAILURE HANDLING: SCREENSHOT & RECOVERY
    # =========================================================================
    except Exception as e:
        # We catch ANY error (timeout, assertion failure, missing keys)
        print(f"\n[FAILED] Test execution crashed or failed an assertion!")
        print(f"[ERROR DETAILS] {e}")

        # 1. Take the screenshot immediately
        take_failure_screenshot(test_name)

        # 2. Force the device back to the idle screen
        print("[RECOVERY] Attempting to force device back to idle screen...")
        os.system("adb shell input keyevent 4")
        time.sleep(1)
        os.system("adb shell input keyevent 4")

        # 3. Fail the test cleanly without the massive stack trace
        pytest.fail(f"Test Failed: {e}", pytrace=False)

    finally:
        print(f"[COOLDOWN] Waiting 3 seconds for EloPayLink UI to reset to idle state...\n")
        time.sleep(3)