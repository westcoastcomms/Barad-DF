# Barad-DF Pipeline# Barad-DF pipeline: raw IQ in, one validated result out
import config
import numpy as np
from sim import simulate_iq
from dsp import channel_filter
from framing import measure, measure_jump
from bearing import bearing_from_phases, expected_magnitude


def analyze(iq, freq_hz, slot_len, fs, bw_hz=None, jump_g=0, jump_m=1, guard=0, min_contrast_db=config.DEFAULT_MIN_CONTRAST_DB):
    """Raw IQ block -> dict(valid, reason, method, bearing_deg, rssi_db, contrast_db, magnitude_ratio)
    bw_hz: optional channel filter width in Hz; jump_g, jump_m, guard: widen these when bw_hz is set."""
    if bw_hz is not None:
        iq = channel_filter(iq, fs, bw_hz)
    measured = measure(iq, slot_len, fs, guard=guard)
    if measured["contrast_db"] < min_contrast_db:
        return {"valid": False, "reason": "weak signal", "method": None, "bearing_deg": None, "rssi_db": None, "contrast_db": measured["contrast_db"], "magnitude_ratio": None, }
    bearing, magnitude = bearing_from_phases(measured["phases"])
    ratio = magnitude / expected_magnitude(freq_hz)
    method = "slot"
    if abs(ratio - 1) >= config.SLOT_TOL:
        method = "jump"
        measured_jump = measure_jump(iq, slot_len, fs, g=jump_g, m=jump_m)
        bearing, _ = bearing_from_phases(measured_jump["phases"])
    rssi_db = 10 * np.log10(measured["signal_power"] - measured["blank_power"])
    return {"valid": True, "reason": "", "method": method, "bearing_deg": bearing,
            "rssi_db": rssi_db, "contrast_db": measured["contrast_db"], "magnitude_ratio": ratio}


# iq = simulate_iq(100.0, 146.52e6, n_frames=21, fs=250e3, frame_rate=1000,
#                 snr_db=15, freq_offset_hz=1500, seed=1)[37:]
# print(analyze(iq, 146.52e6, 50, 250e3))
