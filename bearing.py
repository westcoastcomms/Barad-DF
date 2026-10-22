# Barad-DF Bearing Calculation
import numpy as np
# import webapp
# import framing

# Formula: α = arg( Σₖ φₖ · e^{jθₖ} )

antenna_angles_deg = np.array([45, 135, 225, 315], dtype=float)
antenna_angles = np.deg2rad(antenna_angles_deg)

c = 299792458
freq_hz = 146520e3        # webapp.selected_frequency
SIGN = 1  # +1 normal, -1 if the array reads mirrored
OFFSET_DEG = 0.0  # fixed correction in degrees, set during calibration


def wavelength(freq_hz):
    return c / freq_hz


def array_radius(freq_hz):
    if 88e6 <= freq_hz <= 108e6:
        return 0.47  # FM Broadcast
    elif 144e6 <= freq_hz <= 148e6:
        return 0.45  # 2M HAM
    elif 420e6 <= freq_hz <= 450e6:
        return 0.12  # 70cm HAM
    elif 902e6 <= freq_hz <= 928e6:
        return 0.058  # ISM 915 MHz
    else:
        raise ValueError("selected frequency out of band")


def bearing_from_phases(phases):
    initial_phases = np.asarray(phases, dtype=float)
    if initial_phases.shape != antenna_angles.shape:
        raise ValueError(
            f"expected {antenna_angles.shape[0]} phases, got {initial_phases.shape}")
    weighted_vectors = np.exp(1j * antenna_angles) * initial_phases
    resultant = np.sum(weighted_vectors)
    angle_rad = np.angle(resultant)
    magnitude = np.abs(resultant)
    angle_deg = np.rad2deg(angle_rad)
    bearing_deg = (SIGN * angle_deg + OFFSET_DEG) % 360
    return bearing_deg, magnitude


bearing_deg = None
# last_rssi = None
