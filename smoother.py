# Barad-DF bearing smoothing: circular average of the most recent bearings
from collections import deque
import numpy as np


class BearingSmoother:
    """Keeps the last n bearings (degrees) and reports their circular mean and spread."""

    def __init__(self, n=8):
        # the oldest value drops out automatically
        self.bearings = deque(maxlen=n)

    def add(self, bearing_deg):
        self.bearings.append(float(bearing_deg))

    def _mean_vector(self):
        """Average of the bearings as unit vectors, so 359 and 1 meet near 0, not 180."""
        return np.mean(np.exp(1j * np.deg2rad(list(self.bearings))))

    def value(self):
        """Circular mean in degrees [0, 360), or None if nothing is stored."""
        if not self.bearings:
            return None
        deg = float(np.rad2deg(np.angle(self._mean_vector())))
        # rounding first keeps 359.9999999 from showing as 360.0
        return round(deg, 6) % 360

    def spread(self):
        """0 to 1: how tightly the bearings agree (1 = identical), or None if nothing is stored."""
        if not self.bearings:
            return None
        return float(np.abs(self._mean_vector()))

    def std_deg(self):
        """Approximate circular standard deviation in degrees, or None if nothing is stored."""
        r = self.spread()
        if r is None:
            return None
        return float(np.rad2deg(np.sqrt(-2 * np.log(max(r, 1e-12)))))

    def reset(self):
        self.bearings.clear()
