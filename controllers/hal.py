"""Hardware abstraction layer for the Diamond quadruped.

This module implements step #1 of the motion control roadmap:
- Shared PCA9685 controller management.
- Servo joint abstraction with calibration and safety clamping.
- Loading calibration data from ``configs/servos.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Optional

import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import yaml


@dataclass
class ServoCalibration:
    """Metadata describing how to drive an individual servo joint."""

    channel: int
    home_angle: float
    min_angle: float
    max_angle: float
    offset: float = 0.0
    min_pulse: int = 500
    max_pulse: int = 2500

    def clamp(self, angle: float) -> float:
        """Clamp ``angle`` to the calibrated min/max limits."""

        return max(self.min_angle, min(self.max_angle, angle))


@dataclass
class RobotCalibration:
    """Aggregated calibration data for the robot."""

    frequency: int
    legs: Mapping[str, Mapping[str, ServoCalibration]]

    def leg_names(self) -> Iterable[str]:
        return self.legs.keys()

    def joints_for(self, leg_name: str) -> Mapping[str, ServoCalibration]:
        return self.legs[leg_name]


class PCA9685Controller:
    """Manage access to a shared PCA9685 board."""

    def __init__(
        self,
        *,
        frequency: int = 50,
        i2c: Optional[busio.I2C] = None,
        pca: Optional[PCA9685] = None,
        address: int = 0x40,
    ) -> None:
        if pca is None:
            i2c = i2c or busio.I2C(board.SCL, board.SDA)
            pca = PCA9685(i2c, address=address)
        self._pca = pca
        self._pca.frequency = frequency
        self.frequency = frequency

    def channel(self, channel_index: int):
        """Return the underlying PCA9685 channel object."""

        return self._pca.channels[channel_index]

    def release(self) -> None:
        """Release hardware resources when done."""

        if hasattr(self._pca, "deinit"):
            self._pca.deinit()


class ServoJoint:
    """High-level servo wrapper that applies calibration metadata."""

    def __init__(self, name: str, controller: PCA9685Controller, calibration: ServoCalibration) -> None:
        self.name = name
        self.calibration = calibration
        channel = controller.channel(calibration.channel)
        self._servo = servo.Servo(
            channel,
            min_pulse=calibration.min_pulse,
            max_pulse=calibration.max_pulse,
        )
        self._last_commanded: Optional[float] = None

    @property
    def last_commanded(self) -> Optional[float]:
        return self._last_commanded

    def set_offset(self, offset_deg: float) -> None:
        """Adjust the calibration offset and re-home the servo."""

        self.calibration.offset = offset_deg
        self.move_to_home()

    def set_angle(self, angle_deg: float) -> float:
        """Command the servo to ``angle_deg`` respecting limits and offset."""

        commanded = self.calibration.clamp(angle_deg + self.calibration.offset)
        self._servo.angle = commanded
        self._last_commanded = commanded
        return commanded

    def move_to_home(self) -> float:
        """Return the servo to its calibrated home position."""

        return self.set_angle(self.calibration.home_angle)


def _parse_servo_calibration(servo_data: MutableMapping[str, object]) -> ServoCalibration:
    try:
        channel = int(servo_data["channel"])
        home = float(servo_data["home"])  # type: ignore[index]
        min_angle = float(servo_data.get("min", 0))
        max_angle = float(servo_data.get("max", 180))
    except KeyError as exc:  # pragma: no cover - configuration error surface
        raise ValueError(f"Servo calibration missing required field: {exc}") from exc

    return ServoCalibration(
        channel=channel,
        home_angle=home,
        min_angle=min_angle,
        max_angle=max_angle,
        offset=float(servo_data.get("offset", 0.0)),
        min_pulse=int(servo_data.get("min_pulse", 500)),
        max_pulse=int(servo_data.get("max_pulse", 2500)),
    )


def load_robot_calibration(path: Path | str) -> RobotCalibration:
    """Load servo calibration metadata from ``path``."""

    raw_path = Path(path)
    with raw_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, MutableMapping):  # pragma: no cover - configuration validation
        raise ValueError("Servo calibration file must contain a mapping at the top level")

    frequency = int(data.get("frequency", 50))
    legs_raw = data.get("legs", {})
    legs: Dict[str, Dict[str, ServoCalibration]] = {}
    for leg_name, joints in legs_raw.items():
        if not isinstance(joints, MutableMapping):
            raise ValueError(f"Leg '{leg_name}' must map joint names to calibration data")
        legs[leg_name] = {
            joint_name: _parse_servo_calibration(joint_data)
            for joint_name, joint_data in joints.items()
        }
    return RobotCalibration(frequency=frequency, legs=legs)
