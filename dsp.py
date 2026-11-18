# Barad-DF DSP Helper
from scipy import signal
import numpy as np


def decimate_iq(iq, factor=8, trim=20):
    sample = signal.resample_poly(iq, 1, factor)
    decimated = sample[trim:-trim]
    return decimated


def channel_filter(iq, fs, bw_hz, n_taps=129):
    """Low-pass filter a complex IQ block to a channel bw_hz wide, centred on 0 Hz."""
    taps = signal.firwin(n_taps, bw_hz / 2, fs=fs)
    return np.convolve(iq, taps, mode="valid")


def front_end(raw_iq, capture_fs, decimation, tune_offset_hz):
    """Raw SDR block -> baseband block at capture_fs / decimation, signal centred on 0 Hz."""
    sample_time = np.arange(len(raw_iq)) / capture_fs
    shifted = raw_iq * np.exp(2j * np.pi * tune_offset_hz * sample_time)
    return decimate_iq(shifted, decimation)
