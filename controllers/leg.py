from controllers.servo import Servo

# Leg configuration mapping leg names to servo channels
LEG_CONFIG = {
    "front_left": {
        "lower_hip": 0,
        "upper_hip": 1,
        "shoulder": 2,
        "reset": [52, 85, 84],
        "up": [42, 65, 84],
    },
    "back_left": {
        "lower_hip": 4,
        "upper_hip": 5,
        "shoulder": 6,
        "reset": [49, 80, 95],
        "up": [39, 60, 95],
    },
    "back_right": {
        "lower_hip": 8,
        "upper_hip": 9,
        "shoulder": 10,
        "reset": [128, 88, 97],
        "up": [138, 68, 97],
    },
    "front_right": {
        "lower_hip": 12,
        "upper_hip": 13,
        "shoulder": 14,
        "reset": [129, 90, 75],
        "up": [139, 70, 75],
    },
}

class Leg:
    def __init__(self, name, pca):
        if name not in LEG_CONFIG:
            raise ValueError(f"Invalid leg name: {name}. Must be one of {list(LEG_CONFIG.keys())}")

        self.name = name
        self.config = LEG_CONFIG[name]
        self.shoulder = Servo(self.config["shoulder"], pca)
        self.upper_hip = Servo(self.config["upper_hip"], pca)
        self.lower_hip = Servo(self.config["lower_hip"], pca)

        self.reset()

    @property
    def angles(self):
        return self.lower_hip.angle, self.upper_hip.angle, self.shoulder.angle

    @angles.setter
    def angles(self, angles):
        self.lower_hip.angle = angles[0]
        self.upper_hip.angle = angles[1]
        self.shoulder.angle = angles[2]

    def reset(self):
        self.angles = self.config["reset"]

    def up(self):
        self.angles = self.config["up"]

    def forward_kinematics(self, shoulder_angle, upper_hip_angle, lower_hip_angle):
        pass

    def inverse_kinematics(self, x, y, z):
        pass
