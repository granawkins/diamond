from typing import Optional
from controllers.leg import Leg
from controllers.battery import Battery
from gait import compute_offset_trot

class Body:
    def __init__(self, mode="SIM"):
        self.mode = mode

        self.battery = Battery(mode)
        self.legs = {
            "front_left": Leg("front_left", mode),
            "back_left": Leg("back_left", mode),
            "back_right": Leg("back_right", mode),
            "front_right": Leg("front_right", mode),
        }
        self.default_positions = {name: leg.position[-1] for name, leg in self.legs.items()}

        self.gait: str | None = None
        self.phase = 0.0
        self.target_positions = {name: pos for name, pos in self.default_positions.items()}
        self.speed = 0.05 # of phase update (/1)
        self.max_speed = 10 # of movement in each axis (mm/s)

    def state(self):
        return {
            "legs": {name: leg.state() for name, leg in self.legs.items()},
            "battery": self.battery.state()
        }

    def command(self, cmd: str):
        if cmd == "reset":
            self.reset()
        elif cmd == "walk_forward":
            self.gait = "trot"
        elif cmd == "stop":
            self.gait = None
        elif cmd.startswith("set_"):
            parts = cmd.split("_")
            leg_name = '_'.join(parts[1:3])  # e.g. 'front_left'
            joint_name = '_'.join(parts[3:-2])  # e.g. 'shoulder', 'upper_hip'
            attribute = parts[-2]
            value = float(parts[-1])
            try:
                joint = getattr(self.legs[leg_name], joint_name)
                setattr(joint, attribute, value)
            except (AttributeError, ValueError) as e:
                print(f"Error processing command: {cmd} - {e}")

    def update(self):
        """Update gait state and leg positions. Call this each main loop iteration."""
        self.phase += self.speed
        if self.phase >= 1.0:
            self.phase -= 1.0

        if self.gait is not None:
            # Compute target positions from gait
            for leg_name, default_pos in self.default_positions.items():
                self.target_positions[leg_name] = compute_offset_trot(
                    self.phase, leg_name, default_pos, self.speed
                )
        else:
            for leg_name, default_pos in self.default_positions.items():
                self.target_positions[leg_name] = default_pos

        # Move towards target positions at most at max_speed
        for leg_name, leg in self.legs.items():
            current_pos = leg.position[-1]  # End effector position
            target_pos = self.target_positions[leg_name]
            if current_pos == target_pos:
                continue
            new_pos = tuple(
                current_pos[i] + min(self.max_speed, (target_pos[i] - current_pos[i]))
                for i in range(3)
            )
            leg.position = new_pos

    def reset(self):
        """Reset all legs to default position"""
        self.gait = None
        self.target_positions = {
            name: self.default_positions[name] for name in self.legs
        }
