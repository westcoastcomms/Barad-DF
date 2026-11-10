# Barad-DF Pipeline# Barad-DF pipeline: raw IQ in, one validated result out
import numpy as np
from sim import simulate_iq
from framing import measure, measure_jump
from bearing import bearing_from_phases, expected_magnitude

MIN_CONTRAST_DB = 6.0     # below this the signal is too weak for a usable bearing
# slot-mean is trusted only when the magnitude is this close to expected
SLOT_TOL = 0.10


def analyze(iq, freq_hz, slot_len, fs):
    """Raw IQ block -> dict(valid, reason, method, bearing_deg, rssi_db, contrast_db, magnitude_ratio)"""
    measured = measure(iq, slot_len, fs, guard=0)
    if measured["contrast_db"] < MIN_CONTRAST_DB:
        return {"valid": False, "reason": "weak signal", "method": None, "bearing_deg": None, "rssi_db": None, "contrast_db": measured["contrast_db"], "magnitude_ratio": None, }
    bearing, magnitude = bearing_from_phases(measured["phases"])
    ratio = magnitude / expected_magnitude(freq_hz)
    method = "slot"
    if abs(ratio - 1) >= SLOT_TOL:
        method = "jump"
        measured_jump = measure_jump(iq, slot_len, fs, g=0, m=1)
        bearing, _ = bearing_from_phases(measured_jump["phases"])
    rssi_db = 10 * np.log10(measured["signal_power"] - measured["blank_power"])
    return {"valid": True, "reason": "", "method": method, "bearing_deg": bearing,
            "rssi_db": rssi_db, "contrast_db": measured["contrast_db"], "magnitude_ratio": ratio}


iq = simulate_iq(100.0, 146.52e6, n_frames=21, fs=250e3, frame_rate=1000,
                 snr_db=15, freq_offset_hz=1500, seed=1)[37:]
print(analyze(iq, 146.52e6, 50, 250e3))
