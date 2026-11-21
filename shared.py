# Barad-DF shared state: the capture loop and the web app both use it, always under the lock
import threading
import config

state = {
    "freq_hz": config.DEFAULT_FREQ_HZ,
    "rssi_threshold_dbfs": config.DEFAULT_RSSI_THRESHOLD_DBFS,
    "result": None,
}
state_lock = threading.Lock()
