# Barad-DF CoT thread: once per period, send the receiver position and the current line of bearing to ATAK
import threading
import time
import config
from cot import CotSender, build_lob_event, build_sensor_event
from gps import GpsReader
from shared import state, state_lock


def run_cot_loop(stop_event=None, gps=None, sender=None):
    if gps is None:
        gps = GpsReader(config.GPSD_HOST, config.GPSD_PORT)
        gps.start()
    if sender is None:
        sender = CotSender(config.COT_ADDRESS,
                           config.COT_PORT, config.COT_INTERFACE_IP)
    stop_event = stop_event or threading.Event()
    while not stop_event.is_set():
        with state_lock:
            result = state["result"]
            freq_hz = state["freq_hz"]
        fix = gps.latest()
        if fix is not None:                                              # no position, nothing to draw
            sender.send(build_sensor_event(f"{config.COT_UID_PREFIX}-sensor", fix["lat"], fix["lon"],
                                           fix["hae"], config.COT_CALLSIGN))
            fresh = result is not None and time.time() - result.get("time",
                                                                    0) < config.COT_STALE_S
            if fresh and result.get("smoothed_bearing_deg") is not None:
                true_bearing = (
                    result["smoothed_bearing_deg"] + config.ARRAY_HEADING_DEG) % 360
                rssi = result.get("rssi_db")
                std = result.get("bearing_std_deg")
                remarks = f"{freq_hz / 1e6:.3f} MHz"
                if rssi is not None:
                    remarks += f"  RSSI {rssi:.1f} dBFS"
                if std is not None:
                    remarks += f"  +/-{std:.1f} deg"
                sender.send(build_lob_event(f"{config.COT_UID_PREFIX}-lob", fix["lat"], fix["lon"], fix["hae"],
                                            true_bearing, config.LOB_LENGTH_M, config.COT_CALLSIGN,
                                            remarks, config.COT_STALE_S))
        stop_event.wait(config.COT_PERIOD_S)
