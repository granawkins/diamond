import math
from copy import deepcopy

from controllers.joint import Joint
from kinematics import (
    forward_kinematics, 
    degree_to_radians,
    radians_to_degrees,
)

# Back Left leg
DEFAULT_DH_PARAMS = [
  { "alpha": 0, "a": 0, "d": 15.5, "theta": math.pi / 2 },
  { "alpha": -math.pi / 2, "a": -9.3, "d": 21.1, "theta": -2.1 },
  { "alpha": 0, "a": 63.25, "d": 0, "theta": -2 },
  { "alpha": 0, "a": 82.5, "d": 0, "theta": 0 },
]
OFFSET_Z = 46.5
OFFSET_X = -27.9

class Leg:
    def __init__(self, name, mode="SIM"):
        self.name = name
        self.dh_params = deepcopy(DEFAULT_DH_PARAMS)
        self.offset_z = OFFSET_Z
        self.offset_x = OFFSET_X
        if "front" in name:
            self.dh_params[0]["d"] *= -1
            self.offset_z *= -1
        if "right" in name:
            self.dh_params[1]["d"] *= -1
            self.offset_x *= -1

        self.shoulder = Joint(f"{name}_shoulder", mode)
        self.upper_hip = Joint(f"{name}_upper_hip", mode)
        self.lower_hip = Joint(f"{name}_lower_hip", mode)

        self.shoulder.default = radians_to_degrees(self.dh_params[0]["theta"])
        self.upper_hip.default = radians_to_degrees(self.dh_params[1]["theta"])
        self.lower_hip.default = radians_to_degrees(self.dh_params[2]["theta"])
        self.reset()

    def reset(self):
        self.shoulder.reset()
        self.upper_hip.reset()
        self.lower_hip.reset()
        self.forward_kinematics()

    def state(self):
        return {
            "shoulder": self.shoulder.angle,
            "upper_hip": self.upper_hip.angle,
            "lower_hip": self.lower_hip.angle,
            "positions": self.positions,
        }

    @property
    def angles(self):
        return self.shoulder.angle, self.upper_hip.angle, self.lower_hip.angle

    @angles.setter
    def angles(self, angles):
        self.shoulder.angle = angles[0]
        self.upper_hip.angle = angles[1]
        self.lower_hip.angle = angles[2]
        self.forward_kinematics()

    # def up(self):
    #     x, y, z = self.angles
    #     value = -5 if "right" in self.name else 5
    #     self.angles = (x+value, y-value, z)

    # def down(self):
    #     x, y, z = self.angles
    #     value = -5 if "right" in self.name else 5
    #     self.angles = (x-value, y+value, z)

    def forward_kinematics(self):
        # Derive DH params for this leg
        dh_params = []
        for i, joint in enumerate(self.dh_params):
            theta_deg = 0 if i > 2 else self.angles[i]
            theta_rad = degree_to_radians(theta_deg)
            dh_params.append((joint["alpha"], joint["a"], joint["d"], theta_rad))
        # Calculate the end-effector position
        positions = forward_kinematics(dh_params)
        for pos in positions:
            pos[0] += self.offset_x
            pos[2] += self.offset_z
        self.positions = positions

    def inverse_kinematics(self, x, y, z):
        pass
