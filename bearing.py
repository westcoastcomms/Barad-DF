# Barad-DF Bearing Calculation
import numpy as np
import config

# Formula: α = arg( Σₖ φₖ · e^{jθₖ} )

antenna_angles_deg = np.array(config.ANTENNA_ANGLES_DEG, dtype=float)
antenna_angles = np.deg2rad(antenna_angles_deg)

c = 299792458


def wavelength(freq_hz):
    return c / freq_hz


def array_radius(freq_hz):
    return config.get_band(freq_hz)["radius_m"]


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
    bearing_deg = (config.BEARING_SIGN * angle_deg +
                   config.BEARING_OFFSET_DEG) % 360
    return bearing_deg, magnitude


def expected_magnitude(freq_hz):
    return 4 * np.pi * array_radius(freq_hz) / wavelength(freq_hz)
