# Barad-DF IQ Simulator
import numpy as np
from bearing import antenna_angles, array_radius, wavelength


def generate_phases(true_bearing_deg, freq_hz):
    bearing_rad = np.deg2rad(true_bearing_deg)
    radius = array_radius(freq_hz)
    calculated_wavelength = wavelength(freq_hz)
    A = 2 * np.pi * radius / calculated_wavelength
    phases = np.cos(antenna_angles - bearing_rad) * A
    return phases


def simulate_iq(true_bearing_deg, freq_hz, n_frames=20, fs=250e3,
                frame_rate=1000, snr_db=None, common_phase=0.0, seed=None,
                freq_offset_hz=0.0, static_offsets_rad=None):
    slot_len = int(round(fs / (frame_rate * 5)))
    phases = generate_phases(true_bearing_deg, freq_hz) + common_phase
    if static_offsets_rad is not None:
        phases = phases + np.asarray(static_offsets_rad, dtype=float)
    # each phase repeated slot_len times
    step1 = np.repeat(phases, slot_len)
    # phases become complex samples
    step2 = np.exp(1j * step1)
    blank = np.zeros(slot_len, dtype=complex)     # the blank slot
    frame = np.concatenate((step2, blank))        # one frame = 5 slots
    iq = np.tile(frame, n_frames)                 # n_frames frames

    if freq_offset_hz != 0.0:                     # carrier frequency offset: phase ramp over the whole stream
        n = np.arange(len(iq))
        iq = iq * np.exp(2j * np.pi * freq_offset_hz * n / fs)

    if snr_db is not None:                        # complex white noise; signal power is 1 in the antenna slots
        rng = np.random.default_rng(seed)
        sigma = np.sqrt(10 ** (-snr_db / 10) / 2)
        iq = iq + sigma * (rng.standard_normal(len(iq)) +
                           1j * rng.standard_normal(len(iq)))
    return iq


if __name__ == "__main__":
    iq = simulate_iq(45.0, 146.52e6)
    print(len(iq))
