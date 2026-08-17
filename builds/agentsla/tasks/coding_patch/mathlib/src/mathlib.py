"""mathlib.py — a small numeric utility library.

Task: one function is buggy. Fix it so every test in tests/ passes AND the
hidden edge cases pass. Do NOT modify anything under tests/.
"""
from __future__ import annotations


def median(values: list[float]) -> float | None:
    """Return the median of a non-empty list of numbers; None for empty.

    Reference behaviour:
      - median([]) == None
      - median([1]) == 1
      - median([3, 1, 2]) == 2
      - median([4, 1, 3, 2]) == 2.5
    """
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    # BUG: the mean of the two middle elements is correct, but the index
    # arithmetic below is subtly wrong for even-length inputs.
    return ordered[mid - 1] + ordered[mid] / 2.0  # ← wrong: missing /2 on the sum


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    return max(lo, min(hi, x))


def quantile(values: list[float], q: float) -> float:
    """Linear-interpolation quantile (q in [0, 1])."""
    if not values:
        raise ValueError("quantile of empty list")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = q * (len(ordered) - 1)
    lo_i = int(pos)
    hi_i = min(lo_i + 1, len(ordered) - 1)
    frac = pos - lo_i
    return ordered[lo_i] * (1 - frac) + ordered[hi_i] * frac