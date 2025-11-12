import math
from typing import Tuple

Vec3 = Tuple[float, float, float]


def compute_offset_trot(
    phase: float, 
    leg_name: str,
    default_position: Vec3,
    speed: float = 0.05,
    stride_length: float = 30,
    step_height: float = 15,
) -> Vec3:
    # Diagonal pair assignments for trot gait
    # Pair 1: front_left + back_right (phase 0.0-1.0)
    # Pair 2: front_right + back_left (phase offset by 0.5)
    if leg_name in ["front_left", "back_right"]:
        leg_phase = phase
    else:  # front_right, back_left
        leg_phase = (phase + 0.5) % 1.0

    # Determine if in stance (on ground) or swing (in air)
    # Stance: 0.0-0.5, Swing: 0.5-1.0
    is_swing = leg_phase >= 0.5

    if is_swing:
        # Swing phase: lift foot, move forward, lower down
        swing_progress = (leg_phase - 0.5) * 2  # Normalize to 0-1

        # X: move from back to front of stride (prepare for next step)
        stride_x = -stride_length / 2 + swing_progress * stride_length

        # Z: elliptical arc - lift UP in middle of swing (positive Z)
        stride_z = step_height * math.sin(swing_progress * math.pi)

    else:
        # Stance phase: foot on ground, moves backward (pushes body forward)
        stance_progress = leg_phase * 2  # Normalize to 0-1

        # X: move from front to back of stride (push body forward)
        stride_x = stride_length / 2 - stance_progress * stride_length

        # Z: stay on ground
        stride_z = 0

    # Apply offset to default position
    x = default_position[0] + stride_x
    y = default_position[1]  # No lateral movement
    z = default_position[2] + stride_z

    return (x, y, z)
