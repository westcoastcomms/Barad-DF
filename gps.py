# Barad-DF GPS: reads the position from gpsd in a background thread
import json
import socket
import threading
import time


class GpsReader(threading.Thread):
    """Keeps the latest position fix from gpsd. latest() returns it, or None if there is no recent fix."""

    def __init__(self, host="127.0.0.1", port=2947):
        super().__init__(daemon=True)
        self.host, self.port = host, port
        self._fix = None
        self._lock = threading.Lock()

    def latest(self, max_age_s=10):
        with self._lock:
            fix = self._fix
        if fix is None or time.time() - fix["received"] > max_age_s:
            return None
        return dict(fix)

    def run(self):
        while True:
            try:
                self._session()
            except OSError:
                pass                                  # gpsd not running, or the connection dropped
            with self._lock:
                self._fix = None
            time.sleep(2)                             # then try again

    def _session(self):
        with socket.create_connection((self.host, self.port), timeout=10) as sock:
            sock.sendall(b'?WATCH={"enable":true,"json":true}\n')
            for line in sock.makefile("r"):
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if msg.get("class") != "TPV":
                    continue
                if msg.get("mode", 0) >= 2 and "lat" in msg and "lon" in msg:     # 2D or 3D fix
                    hae = msg.get("altHAE", msg.get("alt"))
                    fix = {"lat": msg["lat"], "lon": msg["lon"],
                           # 9999999 is CoT's "unknown"
                           "hae": 9999999.0 if hae is None else float(hae),
                           "mode": msg["mode"], "received": time.time()}
                else:
                    fix = None                                                  # gpsd reports no fix
                with self._lock:
                    self._fix = fix
