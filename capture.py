# Barad-DF Raw IQ Framing Feature
from rtlsdr import RtlSdr
import webapp

sdr = RtlSdr()

# Configure SDR basic parameters
sdr.sample_rate = 1.024e6  # Hz
sdr.center_freq = webapp.selected_frequency  # Hz
sdr.freq_correction = 60  # PPM
sdr.gain_mode = True
sdr.gain = 29.7  # set slider range between 20.0-40.2

# Set antenna switching rate
antenna_switching_rate = 1000  # Hz
