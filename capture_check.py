# Test Barad-DF Capture Function
import numpy as np
import matplotlib.pyplot as plt
import capture

freq_hz = 99.5e6
gain_db = 29.7
sdr = capture.open_sdr(freq_hz, fs=250e3)

try:
    print(f"Sample Rate: {sdr.sample_rate}, Gain: {sdr.gain}")
    iq = capture.read_iq(sdr)
    print(f"IQ Dtype: {iq.dtype}, IQ Shape: {iq.shape}")
    mean_power = np.mean(np.abs(iq))
    print(f"Mean Power: {mean_power}")
    peak = np.max(np.abs(iq))
    print(f"Peak: {peak}")
    dc_offset = np.abs(np.mean(iq))
    print(f"DC offset: {dc_offset}")
    plt.psd(iq, NFFT=1024, Fs=250e3/1e6, Fc=99.5)
    plt.show()

    # print(dtype, shape, mean power, max iq)

finally:
    capture.close_sdr(sdr)
