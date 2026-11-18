# Barad-DF Main Loop
from unittest import result

import config
import threading
import math
import time
from smoother import BearingSmoother
from capture import open_sdr, read_iq, close_sdr
from dsp import front_end
from pipeline import analyze
import smoother


def process_block(raw_iq, freq_hz):
    """One raw block -> one result dictionary."""
    band = config.get_band(freq_hz)
    baseband = front_end(raw_iq, config.CAPTURE_FS,
                         config.DECIMATION, band["tune_offset_hz"])
    return analyze(baseband, freq_hz, config.SLOT_LEN, config.FS, bw_hz=band["bw_hz"],
                   jump_g=band["jump_g"], jump_m=band["jump_m"], guard=band["guard"],
                   min_contrast_db=band["min_contrast_db"])


state = {"freq_hz": config.DEFAULT_FREQ_HZ, "result": None}
state_lock = threading.Lock()


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
            band = config.get_band(freq_hz)
            tune_hz = freq_hz + band["tune_offset_hz"]
            # old bearings belong to the old frequency
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
            try:
                raw = read_iq(sdr, block_size)
            except OSError:
                close_sdr(sdr)
                sdr = None                       # reopened at the top of the next pass
                continue
            result = process_block(raw, freq_hz)
            if result["valid"]:
                smoother.add(result["bearing_deg"])
                last_valid = time.time()
            elif last_valid is not None and time.time() - last_valid > config.STALE_SECONDS:
                # no valid result for a while: drop the old bearing
                smoother.reset()
            result["smoothed_bearing_deg"] = smoother.value()
            result["bearing_std_deg"] = smoother.std_deg()
            with state_lock:
                state["result"] = result
            if result["valid"]:
                print(
                    f"{result['bearing_deg']:6.1f} deg  rssi {result['rssi_db']:6.1f} dB  {result['method']}  contrast {result['contrast_db']:.1f} dB")
            else:
                print(
                    f"{result['reason']}  contrast {result['contrast_db']:.1f} dB")
            count += 1
    finally:
        if sdr is not None:
            close_sdr(sdr)


if __name__ == "__main__":
    run_loop()
