import pytest
from core.ws_client import EloWebSocketClient
from core.adb_manager import AdbManager


# 1. This hook tells Pytest to accept our custom terminal commands
def pytest_addoption(parser):
    parser.addoption(
        "--device-ip", action="store", default="10.42.0.82", help="IP address of the Elo device"
    )
    parser.addoption(
        "--model", action="store", default="M100", help="Device model (M100, M60, 7Pay)"
    )


# 2. Update the WebSocket fixture to use the dynamic IP
# CHANGED SCOPE TO "function" SO IT OPENS A FRESH CONNECTION FOR EVERY SCENARIO
@pytest.fixture(scope="function")
def ws_client(request):
    device_ip = request.config.getoption("--device-ip")
    port = 6000

    client = EloWebSocketClient(host=device_ip, port=port, timeout=15)
    client.connect()
    yield client
    client.close()


# 3. Create a new fixture for the ADB Manager
# SCOPE REMAINS "session" SO ADB ONLY CONNECTS ONCE AT THE VERY BEGINNING
@pytest.fixture(scope="session")
def adb_manager(request):
    device_ip = request.config.getoption("--device-ip")
    # Initialize and auto-connect ADB using the dynamic IP
    adb = AdbManager(device_ip=device_ip)
    yield adb