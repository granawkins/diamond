"""CLI utility to command individual servos for calibration."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from controllers.hal import PCA9685Controller, RobotCalibration, ServoJoint, load_robot_calibration


def _build_joint(
    controller: PCA9685Controller,
    calibration: RobotCalibration,
    leg: str,
    joint: str,
) -> ServoJoint:
    try:
        joint_cal = calibration.joints_for(leg)[joint]
    except KeyError as exc:
        available_legs = ", ".join(sorted(calibration.leg_names()))
        raise SystemExit(
            f"Unknown leg/joint '{leg}/{joint}'. Available legs: {available_legs}"
        ) from exc
    return ServoJoint(f"{leg}:{joint}", controller, joint_cal)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("leg", help="Leg name as defined in configs/servos.yaml")
    parser.add_argument("joint", help="Joint name within the selected leg")
    parser.add_argument(
        "angle",
        type=float,
        nargs="?",
        help="Angle in degrees to command. If omitted, the joint moves to home.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/servos.yaml"),
        help="Path to the servo calibration YAML file.",
    )
    parser.add_argument(
        "--offset",
        type=float,
        help="Optional offset in degrees to apply before moving the servo.",
    )

    args = parser.parse_args(argv)

    calibration = load_robot_calibration(args.config)
    controller = PCA9685Controller(frequency=calibration.frequency)

    joint = _build_joint(controller, calibration, args.leg, args.joint)
    if args.offset is not None:
        joint.set_offset(args.offset)

    if args.angle is None:
        commanded = joint.move_to_home()
    else:
        commanded = joint.set_angle(args.angle)
    print(f"Commanded {joint.name} to {commanded:.2f}°")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
