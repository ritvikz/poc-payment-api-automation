import subprocess
import time
import logging


class AdbManager:
    def __init__(self, device_ip: str):
        self.device_ip = device_ip
        self.connect_adb()

    def connect_adb(self):
        logging.info(f"ADB: Attempting to connect to {self.device_ip}:5555...")
        try:
            subprocess.run(["adb", "connect", f"{self.device_ip}:5555"], check=True, capture_output=True)

            logging.info("ADB: Connected successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB: Failed to connect. Error: {e.stderr.decode()}")

    def enter_pinpad_data(self, pin_string: str, submit_x: str, submit_y: str):

        pin_map = {
            '1': ('1170', '285'),
            '2': ('1457', '249')
        }

        try:
            time.sleep(2)

            logging.info(f"ADB: Tapping PIN pad for sequence '{pin_string}'...")
            for char in pin_string:
                if char in pin_map:
                    x, y = pin_map[char]
                    subprocess.run(["adb", "-s", f"{self.device_ip}:5555", "shell", "input", "tap", x, y], check=True)
                    time.sleep(0.2)
                else:
                    logging.warning(f"Character '{char}' not in pin_map. Skipping.")

            time.sleep(1)

            logging.info(f"ADB: Tapping Submit at X:{submit_x} Y:{submit_y}...")
            subprocess.run(["adb", "-s", f"{self.device_ip}:5555", "shell", "input", "tap", submit_x, submit_y],
                           check=True)

        except subprocess.CalledProcessError as e:
            logging.error(f"ADB Command failed: {e}")