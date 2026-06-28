# EloPayLink POS Automation Framework

## 📖 Overview
This repository contains a robust, hybrid Point-of-Sale (POS) automation framework designed specifically for the EloPayLink Android application. It acts as a **hardware-in-the-loop** testing engine, bridging the gap between backend WebSocket API payloads and physical hardware UI manipulation.

By utilizing multi-threading, this framework synchronizes software-level API commands with physical screen interactions (via Android Debug Bridge) to execute complex, headless regression scenarios on physical Elo devices (e.g., Elo M100, M60, 7Pay).

> ⚡ This POC was reviewed, approved, and adopted by the client organization for production-level regression testing.

---

## 🚀 Key Architectural Achievements

- **Concurrent Execution (Multi-threading):** Built a dual-channel engine using Python's native `threading` to handle physical UI interactions in the background while simultaneously transmitting and validating TCP/IP WebSocket payloads.

- **Data-Driven Testing (DDT):** Completely decoupled test logic from test data. Scenarios and dynamic payloads are managed via external JSON files (`dataentry_scenarios.json`), allowing QA to scale test coverage without modifying Python code.

- **Self-Healing & State Management:** Engineered a resilient `try/except` recovery net. If a test encounters an unexpected UI state (like a validation popup or timeout), the framework automatically intercepts the error and fires hardware-level teardown commands (Android `keyevent 4`) to reset the device to an idle state, preventing cascading test failures.

- **Automated Evidence Collection:** Integrated automated ADB screen-capturing (`screencap`) that dynamically pulls photographic evidence of the physical device screen to a local `/reports` folder the moment an assertion or timeout fails.

- **Dynamic UI Validation:** Bypassed brittle X/Y coordinate tapping by dumping and parsing the Android XML DOM (`uiautomator dump`), allowing the framework to validate on-screen rendering (line items, UI popups, text matching) programmatically.

- **PCI Compliance Handling:** Documented and handled kernel-level security constraints (such as `FLAG_SECURE` blocking synthetic ADB touches on secure PIN pad screens), shifting physical card flows to specialized test boundaries or CVM limits.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core language |
| Pytest + pytest-html | Test runner & HTML reporting |
| WebSockets (`websocket-client`) | API protocol & payload validation |
| Android Debug Bridge (ADB) | Hardware interface & device control |
| JSON | Data-driven test scenarios |
| XML ElementTree | UI parsing & on-screen validation |

---

## 📂 Project Structure

```
poc-payment-pos-automation/
├── core/
│   ├── adb_manager.py         # Hardware interactions, swipes, taps, screen capture
│   └── ws_client.py           # WebSocket connections and payload transmission
├── test_data/
│   ├── dataentry.json         # Base JSON payload templates
│   └── dataentry_scenarios.json  # Data-driven test scenarios (Positive & Negative)
├── tests/
│   └── test_dataentry.py      # Main Pytest engine and validation logic
├── reports/                   # Auto-generated HTML reports and failure screenshots
├── requirements.txt           # Python dependencies
└── README.md
```

---

## ⚙️ Prerequisites & Setup

1. Ensure **Python 3.10+** is installed on your local machine.
2. Ensure **Android Platform Tools (ADB)** is installed and added to your system PATH.
3. Install required Python packages:
```bash
pip install pytest pytest-html websocket-client
```
4. Ensure your local machine and the physical Elo device are on the same local network.
5. Connect ADB to the device via TCP/IP:
```bash
adb connect <DEVICE_IP>:5555
```

---

## ▶️ How to Run

Execute the full test suite and generate an HTML report:
```bash
python -m pytest tests/test_dataentry.py --html=reports/report.html -s --tb=short
```

| Flag | Purpose |
|---|---|
| `--html=reports/report.html` | Generates a shareable HTML test report |
| `-s` | Shows terminal print statements during execution |
| `--tb=short` | Clean, concise failure traces for CI/CD logs |

---

## 📊 Test Execution Strategy

The framework validates all scenarios strictly against the expected outcome defined in the JSON file:

- ✅ **Pass:** Verifies WebSocket response codes and UI updates match expected values
- ⚠️ **Validation Popup:** Verifies popup text via XML parsing, clears via ADB, passes the test
- ❌ **Unexpected Crash:** Captures screenshot, forces device recovery, cleanly fails the Pytest run

---

## 👤 Author

**Ritvik Singh Chouhan** — Senior QA Automation Engineer | SDET-II  
🔗 [GitHub](https://github.com/ritvikz) | [Portfolio](https://www.crio.do/learn/portfolio/ritvikchouhan77/)
