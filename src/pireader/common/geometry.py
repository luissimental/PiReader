"""System-wide helper functions for geometric calculations."""


def angular_diff(start_angle: float, end_angle: float) -> float:
    """Calculate the angular difference between two angles in degrees.

    A positive angular difference is counterclockwise.
    A negative angular difference is clockwise.

    Returns:
      The angular difference in degrees normalized into the range of
      [-180º, 180º).

    """
    return (end_angle - start_angle + 180) % 360 - 180
