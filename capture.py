# Barad-DF Raw IQ Capture
from rtlsdr import RtlSdr


def open_sdr(freq_hz, fs=250e3, gain_db=29.7):
    # Configure SDR basic parameters
    sdr = RtlSdr()
    sdr.sample_rate = fs  # Hz
    sdr.center_freq = freq_hz  # Hz
    sdr.set_agc_mode(False)
    sdr.gain = gain_db  # set slider range between 20.0-40.2
    sdr.read_samples(2**14)
    return sdr


def read_iq(sdr, n_samples=2**16):
    # Return n_samples complex samples as 1-d numpy array
    sdr.read_samples(n_samples)
    return sdr.read_samples(n_samples)


def close_sdr(sdr):
    # Release the dongle
    sdr.close()


# Set antenna switching rate
# antenna_switching_rate = 1000  # Hz
