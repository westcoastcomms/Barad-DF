# Send a test line of bearing to ATAK, so the display can be checked without any receiver hardware
import time
import config
from cot import CotSender, build_lob_event, build_sensor_event
from gps import GpsReader

BEARING_DEG = 100.0          # true bearing of the test line
SECONDS = 30                 # how long to keep sending

gps = GpsReader(config.GPSD_HOST, config.GPSD_PORT)
gps.start()
sender = CotSender(config.COT_ADDRESS, config.COT_PORT,
                   config.COT_INTERFACE_IP)

print("waiting for a GPS fix...")
fix = None
while fix is None:
    time.sleep(1)
    fix = gps.latest()
print(f"fix at {fix['lat']:.5f}, {fix['lon']:.5f}")

for _ in range(SECONDS):
    fix = gps.latest() or fix
    sender.send(build_sensor_event(
        f"{config.COT_UID_PREFIX}-sensor", fix["lat"], fix["lon"], fix["hae"], config.COT_CALLSIGN))
    sender.send(build_lob_event(f"{config.COT_UID_PREFIX}-lob", fix["lat"], fix["lon"], fix["hae"], BEARING_DEG,
                                config.LOB_LENGTH_M, config.COT_CALLSIGN, f"test line, bearing {BEARING_DEG:.0f}", config.COT_STALE_S))
    time.sleep(1)
print("done; the line disappears from ATAK after the stale time")
