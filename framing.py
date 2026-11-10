# Barad-DF IQ Framing
import numpy as np


def find_frame_start(iq, slot_len, slots_per_frame=5):
    frame_len = slot_len * slots_per_frame
    samp_power = np.abs(iq) ** 2

    # keep whole frames only and stack them, one row per frame
    n_frames = len(samp_power) // frame_len
    frames = samp_power[:n_frames * frame_len].reshape(n_frames, frame_len)

    # average the rows: the repeating pattern stays, the noise shrinks
    folded = frames.mean(axis=0)

    # slide a one-slot-wide window along the pattern, wrapping around the end
    wrapped = np.concatenate((folded, folded[:slot_len - 1]))
    window_sums = np.convolve(wrapped, np.ones(slot_len), mode='valid')

    # the lowest window sits on the blank slot; the frame starts one slot later
    blank_start = np.argmin(window_sums)
    frame_start = (blank_start + slot_len) % frame_len
    return int(frame_start)


def slice_frames(iq, frame_start, slot_len, slots_per_frame=5):
    # Return the stream as an array shaped (n_frames, slots_per_frame, slot_len).
    frame_len = slot_len * slots_per_frame
    trimmed_stream = iq[frame_start:]
    n_frames = len(trimmed_stream) // frame_len
    trimmed_frames = trimmed_stream[:n_frames * frame_len]
    frames = trimmed_frames.reshape(n_frames, slots_per_frame, slot_len)
    return frames


def estimate_cfo(frames, fs):
    """Carrier frequency offset in Hz: coarse estimate inside the slots, then a fine estimate between frames."""
    n_frames, slots, slot_len = frames.shape
    s = frames[:, :4, :]                                   # antenna slots only
    # coarse: phase step between neighbouring samples of the same slot
    r = np.sum(s[..., 1:] * np.conj(s[..., :-1]))
    f_coarse = np.angle(r) * fs / (2 * np.pi)
    # fine: phase step of the same antenna one frame later
    z = derotate(frames, f_coarse, fs)[:, :4, :].mean(axis=2)
    d = np.sum(z[1:] * np.conj(z[:-1]))
    t_frame = slots * slot_len / fs
    f_fine = np.angle(d) / (2 * np.pi * t_frame)
    return f_coarse + f_fine


def derotate(frames, f, fs):
    """Remove a carrier frequency offset of f Hz from the frames."""
    # flatten to the 1-D stream, multiply by the rotation, reshape back to frames.shape
    flat = frames.reshape(-1)
    n = np.arange(len(flat))
    flattened_stream = flat * np.exp(-2j * np.pi * f * n / fs)
    derotated = flattened_stream.reshape(frames.shape)
    return derotated


def measure_frames(frames, fs, cfo_hz, guard=0):
    """-> phases (4,), signal_power, blank_power"""
    derotated = derotate(frames, cfo_hz, fs)

    # one complex number per antenna slot per frame, shape (n_frames, 4)
    slot_values = derotated[:, :4, guard:].mean(axis=2)

    # remove each frame's shared phase so the four phases sit near zero
    ref = np.angle(slot_values.sum(axis=1, keepdims=True))
    referenced = slot_values * np.exp(-1j * ref)

    # phase of each antenna, averaged over the frames
    phases = np.angle(referenced).mean(axis=0)

    signal_power = np.mean(np.abs(derotated[:, :4, guard:]) ** 2)
    blank_power = np.mean(np.abs(derotated[:, 4, :]) ** 2)
    return phases, signal_power, blank_power


def measure(iq, slot_len, fs, guard=0):
    """Raw IQ stream -> dict with phases, cfo_hz, signal_power, blank_power, frame_start, n_frames"""
    frame_start = find_frame_start(iq, slot_len, slots_per_frame=5)
    frames = slice_frames(iq, frame_start, slot_len, slots_per_frame=5)
    cfo = estimate_cfo(frames, fs)
    phases, signal_power, blank_power = measure_frames(frames, fs, cfo, guard)
    contrast_db = 10 * np.log10(signal_power / blank_power)
    return dict(phases=phases, cfo_hz=cfo, signal_power=signal_power, blank_power=blank_power, frame_start=frame_start, contrast_db=contrast_db, n_frames=frames.shape[0])


def jump_phases(frames, g=0, m=1):
    """Four relative antenna phases from the phase jumps at the antenna-to-antenna boundaries.
    Works on modulated signals. g widens the transition window, m is how many increments are used outside it."""
    n_frames, slots, slot_len = frames.shape
    x = frames.reshape(n_frames, slots * slot_len)
    # phase step from sample n to n+1
    inc = np.angle(x[:, 1:] * np.conj(x[:, :-1]))
    jumps = []
    for k in (1, 2, 3):                                           # boundaries 1->2, 2->3, 3->4
        # first sample of the next slot
        b = k * slot_len
        win = inc[:, b - 1 - g: b + g].sum(axis=1)
        left = inc[:, b - 1 - g - m: b - 1 - g].mean(axis=1)
        right = inc[:, b + g: b + g + m].mean(axis=1)
        # remove what the signal was doing anyway
        jump = win - (2 * g + 1) * 0.5 * (left + right)
        # circular mean over the frames
        jumps.append(np.angle(np.mean(np.exp(1j * jump))))
    return np.concatenate(([0.0], np.cumsum(jumps)))


def measure_jump(iq, slot_len, fs, g=0, m=1):
    """Same job as measure(), using the jump estimator. fs is unused but kept so the two are interchangeable."""
    frame_start = find_frame_start(iq, slot_len)
    frames = slice_frames(iq, frame_start, slot_len)
    return dict(phases=jump_phases(frames, g, m),
                signal_power=np.mean(np.abs(frames[:, :4]) ** 2),
                blank_power=np.mean(np.abs(frames[:, 4]) ** 2),
                frame_start=frame_start, n_frames=frames.shape[0])
