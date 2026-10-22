# Sweep Test Script
import numpy as np
import matplotlib.pyplot as plt
from bearing import bearing_from_phases, array_radius, wavelength, antenna_angles

freq_hz = 146.52e6
true_bearing_deg = 45.0

test_radius = array_radius(freq_hz)
test_wavelength = wavelength(freq_hz)

A = 2 * np.pi * test_radius / test_wavelength


def generate_phases(true_bearing_deg):
    bearing_rad = np.deg2rad(true_bearing_deg)
    phases = np.cos(antenna_angles - bearing_rad) * A
    return phases


test_phases = generate_phases(true_bearing_deg)

returned_values = bearing_from_phases(test_phases)

true_bearings = np.arange(0, 360, 1)
bearing_list = []
magnitude_list = []

for bearing in true_bearings:
    phases = generate_phases(bearing)
    est_bearing, magnitude = bearing_from_phases(phases)
    bearing_list.append(est_bearing)
    magnitude_list.append(magnitude)

bearing_array = np.array(bearing_list)
magnitude_array = np.array(magnitude_list)

computed_error = (bearing_array - true_bearings + 180) % 360 - 180
max_error = np.max(np.abs(computed_error))
print(max_error)
print(np.min(magnitude_array))
print(np.max(magnitude_array))
print(np.min(max_error))
