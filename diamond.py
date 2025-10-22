"""Top-level entry point for commanding the Diamond quadruped."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from controllers.hal import PCA9685Controller, ServoJoint, load_robot_calibration


@dataclass
class DiamondLeg:
    """Bundle of servo joints that comprise a single leg."""

    name: str
    lower_hip: ServoJoint
    upper_hip: ServoJoint
    shoulder: ServoJoint

    def move_to_home(self) -> None:
        self.lower_hip.move_to_home()
        self.upper_hip.move_to_home()
        self.shoulder.move_to_home()


class Diamond:
    """Convenience wrapper for quick manual tests using the HAL."""

    def __init__(self, config_path: Path | str = "configs/servos.yaml") -> None:
        self.config_path = Path(config_path)
        calibration = load_robot_calibration(self.config_path)
        self.controller = PCA9685Controller(frequency=calibration.frequency)

        self.legs: Dict[str, DiamondLeg] = {}
        for leg_name, joints in calibration.legs.items():
            leg = DiamondLeg(
                name=leg_name,
                lower_hip=ServoJoint(f"{leg_name}:lower_hip", self.controller, joints["lower_hip"]),
                upper_hip=ServoJoint(f"{leg_name}:upper_hip", self.controller, joints["upper_hip"]),
                shoulder=ServoJoint(f"{leg_name}:shoulder", self.controller, joints["shoulder"]),
            )
            self.legs[leg_name] = leg

    def reset(self) -> None:
        for leg in self.legs.values():
            leg.move_to_home()

    def up(self) -> None:
        for leg in self.legs.values():
            if "right" in leg.name:
                leg.upper_hip.set_angle(75)
                leg.lower_hip.set_angle(30)
            else:
                leg.upper_hip.set_angle(30)
                leg.lower_hip.set_angle(75)

    def dance(self, times: int) -> None:
        for _ in range(times):
            self.up()
            time.sleep(2)
            self.reset()
            time.sleep(2)

    def shutdown(self) -> None:
        self.controller.release()


if __name__ == "__main__":
    robot = Diamond()
    try:
        robot.dance(1)
    finally:
        robot.shutdown()
