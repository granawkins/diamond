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

    def state(self):
        return {
            "legs": {name: leg.state() for name, leg in self.legs.items()},
            "battery": self.battery.state()
        }

    def update(self):
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
            leg = self.legs[name]
            end_effector = leg.position[-1]
            leg.position = end_effector[0], end_effector[1], end_effector[2] + 5

    def down(self):
        """Update target to move body down"""
        for name in self.legs.keys():
            leg = self.legs[name]
            end_effector = leg.position[-1]
            leg.position = end_effector[0], end_effector[1], end_effector[2] - 5
