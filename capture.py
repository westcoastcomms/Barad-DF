# Barad-DF Raw IQ Framing Feature
import numpy
import webapp
from rtlsdr import RtlSdr


def open_sdr(freq_hz, fs=250e3):
    # Configure SDR basic parameters
    sdr = RtlSdr()
    sdr.sample_rate = 1.024e6  # Hz
    sdr.center_freq = webapp.selected_frequency  # Hz
    sdr.freq_correction = 60  # PPM
    sdr.gain_mode = True
    sdr.gain = 29.7  # set slider range between 20.0-40.2
    # read and throw away one block (frst samples after)


def read_iq(sdr, n_samples=2**16):
    # Return n_samples complex samples as 1-d numpy array
    iq =
    return iq


def close_sdr(sdr):
    # Release the dongle
    return


# Set antenna switching rate
antenna_switching_rate = 1000  # Hz
