import json
import logging
from websocket import create_connection, WebSocketTimeoutException


class EloWebSocketClient:
    def __init__(self, host: str, port: int = 6000, timeout: int = 15):
        self.host = host
        self.port = port
        self.url = f"ws://{self.host}:{self.port}/"
        self.timeout = timeout
        self.ws = None

    def connect(self):
        """Establishes the WebSocket connection to the Elo device."""
        logging.info(f"Attempting to connect to {self.url}")
        try:
            self.ws = create_connection(self.url, timeout=self.timeout)
            logging.info("Connection established successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to {self.url}. Error: {e}")
            raise

    def close(self):
        """Closes the active WebSocket connection."""
        if self.ws:
            self.ws.close()
            logging.info("WebSocket connection closed.")

    def send_json_payload(self, file_path: str) -> dict:
        """Reads a static JSON file from disk, sends it, and returns the response."""
        if not self.ws:
            raise ConnectionError("WebSocket is not connected. Call connect() first.")

        logging.info(f"Sending payload from {file_path}")
        with open(file_path, 'r') as file:
            payload = file.read()

        self.ws.send(payload.encode('utf-8'))

        try:
            response = self.ws.recv()
            return json.loads(response)
        except WebSocketTimeoutException:
            logging.error("WebSocket timed out waiting for a response from the device.")
            raise
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
            raise

    def send_dict_payload(self, payload: dict) -> dict:
        """Takes a dynamic Python dictionary, converts it to JSON, and sends it."""
        if not self.ws:
            raise ConnectionError("WebSocket is not connected. Call connect() first.")

        # Convert the Python dictionary into a tight JSON string format
        input_string = json.dumps(payload, separators=(',', ':'))
        logging.info(f"Sending dynamic payload: {input_string}")

        self.ws.send(input_string.encode('utf-8'))

        try:
            response = self.ws.recv()
            logging.info("Response received.")
            return json.loads(response)
        except WebSocketTimeoutException:
            logging.error("WebSocket timed out waiting for a response.")
            raise
        except Exception as e:
            logging.error(f"WebSocket error while waiting for response: {e}")
            raise