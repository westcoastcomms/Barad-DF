# Barad-DF DSP Helper
from scipy import signal
import numpy as np


def decimate_iq(iq, factor=8, trim=20):
    sample = signal.resample_poly(iq, 1, factor)
    decimated = sample[trim:-trim]
    return decimated
