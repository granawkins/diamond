from controllers.leg import Leg
from controllers.battery import Battery

class Body:
    def __init__(self, mode="SIM"):
        self.mode = mode

        self.legs = {
            "front_left": Leg("front_left", mode),
            "back_left": Leg("back_left", mode),
            "back_right": Leg("back_right", mode),
            "front_right": Leg("front_right", mode),
        }
        self.battery = Battery(mode)

        # Motion smoothing state
        self.target_angles = {name: leg.angles for name, leg in self.legs.items()}
        self.interpolation_speed = 0.3  # 0-1, higher = faster

    def status(self):
        return {
            "legs": {name: leg.angles for name, leg in self.legs.items()},
            "battery": self.battery.status()
        }

    def step(self):
        """Smoothly interpolate towards target angles. Call this each main loop iteration."""
        for name, leg in self.legs.items():
            current = leg.angles
            target = self.target_angles[name]

            # Linear interpolation
            new_angles = tuple(
                current[i] + (target[i] - current[i]) * self.interpolation_speed
                for i in range(3)
            )
            leg.angles = new_angles

    def reset(self):
        """Set target to reset position"""
        for name, leg in self.legs.items():
            leg.reset()
            self.target_angles[name] = leg.angles

    def up(self):
        """Update target to move body up"""
        for name in self.legs.keys():
            current_target = list(self.target_angles[name])
            value = -5 if "right" in name else 5
            current_target[0] += value
            current_target[1] -= value
            self.target_angles[name] = tuple(current_target)

    def down(self):
        """Update target to move body down"""
        for name in self.legs.keys():
            current_target = list(self.target_angles[name])
            value = -5 if "right" in name else 5
            current_target[0] -= value
            current_target[1] += value
            self.target_angles[name] = tuple(current_target)

    def front_up(self):
        """Update target to move front legs up"""
        for name in ["front_left", "front_right"]:
            current_target = list(self.target_angles[name])
            value = -5 if "right" in name else 5
            current_target[0] += value
            current_target[1] -= value
            self.target_angles[name] = tuple(current_target)

    def back_up(self):
        """Update target to move back legs up"""
        for name in ["back_left", "back_right"]:
            current_target = list(self.target_angles[name])
            value = -5 if "right" in name else 5
            current_target[0] += value
            current_target[1] -= value
            self.target_angles[name] = tuple(current_target)