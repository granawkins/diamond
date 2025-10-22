"""Leg-level abstractions and kinematics skeletons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple


@dataclass
class LinkLengths:
    """Container for leg link lengths."""

    hip: float
    thigh: float
    shank: float


class LegKinematics:
    """Placeholder implementation for leg kinematics (roadmap step #2)."""

    def __init__(
        self,
        link_lengths: LinkLengths,
        joint_order: Sequence[str] = ("hip_yaw", "hip_pitch", "knee"),
    ) -> None:
        self.link_lengths = link_lengths
        self.joint_order = tuple(joint_order)

    def forward_kinematics(self, joint_angles: Sequence[float]) -> Tuple[float, float, float]:
        """Compute the foot pose from ``joint_angles``.

        Returns a dummy pose until the analytic solution is implemented.
        """

        _ = joint_angles
        return (0.0, 0.0, 0.0)

    def inverse_kinematics(
        self,
        target_pose: Sequence[float],
        *,
        elbow_up: bool = True,
    ) -> Tuple[float, float, float]:
        """Compute joint angles that realize ``target_pose``.

        Returns placeholder joint angles and will be filled with real math later.
        """

        _ = (target_pose, elbow_up)
        return (0.0, 0.0, 0.0)

    def workspace_hint(self) -> Iterable[str]:
        """Provide human-readable hints about the configured workspace.

        This is a convenience stub to demonstrate how documentation or debug
        helpers could expose constraints. Replace with real limits when
        kinematics are available.
        """

        yield (
            "Workspace limits are not yet enforced; update `LegKinematics` once "
            "IK is implemented."
        )
