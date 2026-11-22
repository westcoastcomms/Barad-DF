# Barad-DF Main Loop
import webapp
import config
import threading
import cot_output
import math
import time
from smoother import BearingSmoother
from capture import open_sdr, read_iq, close_sdr
from dsp import front_end
from pipeline import analyze
from shared import state, state_lock


def process_block(raw_iq, freq_hz):
    """One raw block -> one result dictionary."""
    band = config.get_band(freq_hz)
    baseband = front_end(raw_iq, config.CAPTURE_FS,
                         config.DECIMATION, band["tune_offset_hz"])
    return analyze(baseband, freq_hz, config.SLOT_LEN, config.FS, bw_hz=band["bw_hz"],
                   jump_g=band["jump_g"], jump_m=band["jump_m"], guard=band["guard"],
                   min_contrast_db=band["min_contrast_db"])


def run_loop(max_blocks=None):
    n = (config.FRAMES_PER_BLOCK + 1) * config.FRAME_RAW
    block_size = math.ceil(n / 256) * 256
    sdr, tuned_freq, count = None, None, 0
    smoother = BearingSmoother(config.SMOOTHING_N)      # before the while loop
    last_valid = None
    try:
        while max_blocks is None or count < max_blocks:
            with state_lock:
                freq_hz = state["freq_hz"]
                threshold = state["rssi_threshold_dbfs"]
            band = config.get_band(freq_hz)
            tune_hz = freq_hz + band["tune_offset_hz"]
            smoother.reset()
            if sdr is None:
                sdr = open_sdr(tune_hz, fs=config.CAPTURE_FS)
                sdr.gain = config.GAIN_DB
                tuned_freq = freq_hz
            elif freq_hz != tuned_freq:
                sdr.center_freq = tune_hz
                # discard: the first samples after a retune are unreliable
                read_iq(sdr, 2**14)
                tuned_freq = freq_hz
                smoother.reset()  # old bearings belong to the old frequency
                last_valid = None
            try:
                raw = read_iq(sdr, block_size)
            except OSError:
                close_sdr(sdr)
                sdr = None                       # reopened at the top of the next pass
                continue
            result = process_block(raw, freq_hz)
            if result["valid"] and result["rssi_db"] < threshold:
                result["valid"] = False
                result["reason"] = "below RSSI threshold"
            if result["valid"]:
                smoother.add(result["bearing_deg"])
                last_valid = time.time()
            elif last_valid is not None and time.time() - last_valid > config.STALE_SECONDS:
                # no valid result for a while: drop the old bearing
                smoother.reset()
                last_valid = None
            result["smoothed_bearing_deg"] = smoother.value()
            result["bearing_std_deg"] = smoother.std_deg()
            with state_lock:
                state["result"] = result
            count += 1
    finally:
        if sdr is not None:
            close_sdr(sdr)


if __name__ == "__main__":
    threading.Thread(target=webapp.run_server, daemon=True).start()
    if config.COT_ENABLED:
        threading.Thread(target=cot_output.run_cot_loop)
    run_loop()
