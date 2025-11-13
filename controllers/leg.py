import math
from copy import deepcopy
from typing import List

from controllers.joint import Joint
from kinematics import (
    forward_kinematics,
    inverse_kinematics,
    degree_to_radians,
    radians_to_degrees,
    Vec3,
)

# Back Left leg
DEFAULT_DH_PARAMS = [
  # Base (center of body) to first joint + axis rotation so x=forward, y=left, z=up
  { "alpha": 0, "a": -46.5, "d": 0, "theta": -math.pi / 2 },
  # First joint (shoulder)
  { "alpha": math.pi / 2, "a": -27.9, "d": 15.5, "theta": math.pi / 2 },
  # Second joint (upper hip)
  { "alpha": -math.pi / 2, "a": -9.3, "d": 21.1, "theta": -2.1 },
  # Third joint (lower hip)
  { "alpha": 0, "a": 63.25, "d": 0, "theta": -2 },
  # End effector (foot)
  { "alpha": 0, "a": 82.5, "d": 0, "theta": 0 },
]
OFFSET_Z = 46.5
OFFSET_X = -27.9

class Leg:
    def __init__(self, name, mode="SIM"):
        self.name = name
        self.dh_params = deepcopy(DEFAULT_DH_PARAMS)
        if "front" in name:
            self.dh_params[0]["a"] *= -1
            self.dh_params[1]["d"] *= -1
        if "right" in name:
            self.dh_params[1]["a"] *= -1
            self.dh_params[2]["d"] *= -1

        [t1, t2, t3] = [radians_to_degrees(self.dh_params[i]["theta"]) for i in (1, 2, 3)]
        self.shoulder = Joint(f"{name}_shoulder", t1, mode)
        self.upper_hip = Joint(f"{name}_upper_hip", t2, mode)
        self.lower_hip = Joint(f"{name}_lower_hip", t3, mode)
        self.reset()

    def reset(self):
        self.shoulder.reset()
        self.upper_hip.reset()
        self.lower_hip.reset()

    def state(self):
        return {
            "shoulder": self.shoulder.angle,
            "upper_hip": self.upper_hip.angle,
            "lower_hip": self.lower_hip.angle,
            "positions": self.position,
        }

    @property
    def angles(self):
        return self.shoulder.angle, self.upper_hip.angle, self.lower_hip.angle

    @angles.setter
    def angles(self, angles):
        self.shoulder.angle = angles[0]
        self.upper_hip.angle = angles[1]
        self.lower_hip.angle = angles[2]

    @property
    def position(self) -> List[Vec3]:
        # Derive DH params for this leg\
        angles = [None] + list(self.angles) + [None]
        dh_params = []
        for joint, angle in zip(self.dh_params, angles):
            if angle is not None:
                joint["theta"] = degree_to_radians(angle)
            dh_params.append((joint["alpha"], joint["a"], joint["d"], joint["theta"]))
        # Calculate the end-effector position
        positions = forward_kinematics(dh_params)
        return positions

    @position.setter
    def position(self, position: Vec3):
        # Calculate joint angles using current angles as initial guess
        current_angles = tuple(degree_to_radians(a) for a in self.angles)
        angles = inverse_kinematics(position, self.dh_params, current_angles)
        if angles is None:
            print(f"Failed to calculate inverse kinematics for {self.name}")
            return

        # Convert to degrees and update joints
        self.angles = tuple(radians_to_degrees(a) for a in angles)
