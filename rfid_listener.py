import serial
import json
import threading
import time
from app import selected_image

MAP_FILE = "rfid_map.json"
PORT = "/dev/rfcomm0"   # assumes `rfcomm connect 0 <MAC> 1` is running
BAUD = 115200
RELOAD_INTERVAL = 5     # seconds between reloads of JSON mapping

def load_mapping():
    """Load RFID → image mapping from JSON file."""
    try:
        with open(MAP_FILE, "r") as f:
            mapping = json.load(f)
            if "default" not in mapping:
                print("⚠️  No 'default' key found in rfid_map.json!")
            return mapping
    except Exception as e:
        print("Error loading mapping:", e)
        return {}

def listen_for_rfid():
    """Listen for RFID UIDs from /dev/rfcomm0 and update selected_image."""
    mapping = load_mapping()
    last_load = time.time()
    print("✅ Loaded RFID mapping:", mapping)
    buffer = ""
    current_tag = None

    while True:
        # Periodically reload mapping (so you can edit rfid_map.json live)
        if time.time() - last_load > RELOAD_INTERVAL:
            mapping = load_mapping()
            last_load = time.time()

        try:
            with serial.Serial(PORT, BAUD, timeout=0.1) as bt:
                print(f"🔗 Listening for RFID tags on {PORT}...")
                while True:
                    chunk = bt.read(bt.in_waiting or 1).decode(errors="ignore")
                    if not chunk:
                        time.sleep(0.05)
                        continue

                    buffer += chunk
                    if "\n" in buffer or "\r" in buffer:
                        lines = buffer.replace("\r", "\n").split("\n")
                        buffer = lines[-1]  # leftover partial line

                        for line in lines[:-1]:
                            line = line.strip().upper()
                            if len(line) == 0:
                                continue

                            # Handle explicit "NO_TAG" message from ESP32
                            if line == "NO_TAG":
                                default_img = mapping.get("default")
                                if selected_image["filename"] != default_img:
                                    selected_image["filename"] = default_img
                                    print(f"🕓 Tag removed → Reverting to default image: {default_img}")
                                current_tag = None
                                continue

                            # Regular RFID tag UID
                            if line != current_tag:
                                current_tag = line
                                if line in mapping:
                                    image = mapping[line]
                                    selected_image["filename"] = image
                                    print(f"🎫 RFID read: {line}")
                                    print(f"🖼️  → Displaying image: {image}")
                                else:
                                    print(f"❓ Unknown RFID: {line}")
        except serial.SerialException:
            print("⚠️  /dev/rfcomm0 not available — waiting for reconnection...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(2)

def start_listener():
    """Start the RFID listener thread."""
    thread = threading.Thread(target=listen_for_rfid, daemon=True)
    thread.start()
    print("🚀 RFID listener thread started.")

