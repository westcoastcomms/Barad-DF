# Barad-DF Configuration Parameters

# --- Signal Chain ---
BACKEND = "rtlsdr"              # later: "hackrf"
CAPTURE_FS = 2.0e6              # Hz, raw rate from the SDR
DECIMATION = 8
FS = CAPTURE_FS / DECIMATION    # Hz after decimation
# full antenna cycles per second (depends on the Opera Cake's speed)
ROTATION_HZ = 1000
SLOTS_PER_FRAME = 5             # 4 antennas + 1 blank (terminated) slot
SLOT_LEN = int(FS / (ROTATION_HZ * SLOTS_PER_FRAME))
# samples per slot; must come out a whole number
FRAMES_PER_BLOCK = 250

# --- Capture ---
GAIN_DB = 49.6
# See band dicts for tuning offset tune this far off the signal to dodge the DC spike (0 on a HackRF Pro)


# --- Antenna Array & Switch ---
# B1 holds the 50 ohm terminator (blank slot)
ANTENNA_SWITCH_SEQUENCE = {"A1": 45, "A2": 135,
                           "A3": 225, "A4": 315, "B1": None}

# --- Frequency Bands ---
BANDS = [

    dict(name="FM Broadcast", low_hz=88e6, high_hz=108e6, radius_m=0.47,
         bw_hz=None, jump_g=0, jump_m=1, guard=0, min_contrast_db=3.5, tune_offset_hz=100e3),
    dict(name="2m", low_hz=144e6, high_hz=148e6, radius_m=0.45,
         bw_hz=25e3, jump_g=8, jump_m=3, guard=16, min_contrast_db=3.5, tune_offset_hz=50e3),
    dict(name="70cm", low_hz=420e6, high_hz=450e6, radius_m=0.12,
         bw_hz=25e3, jump_g=8, jump_m=3, guard=16, min_contrast_db=3.5, tune_offset_hz=50e3),
    dict(name="915 MHz", low_hz=902e6, high_hz=928e6, radius_m=0.058,
         bw_hz=None, jump_g=0, jump_m=1, guard=0, min_contrast_db=10, tune_offset_hz=100e3),
]


def get_band(freq_hz):
    """Return the band dict containing freq_hz; raise ValueError if it is outside every band."""
    for band in BANDS:
        if band["low_hz"] <= freq_hz <= band["high_hz"]:
            return band
    raise ValueError(f"Frequency {freq_hz} is outside every band")


# --- Gate ---
SLOT_TOL = 0.10

# --- Output ---
WEB_PORT = 8080
COT_ADDRESS = "239.2.3.1"       # placeholder: check against ATAK's network settings
COT_PORT = 6969                 # placeholder
