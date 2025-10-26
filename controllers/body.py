from controllers.leg import Leg
from controllers.pca import pca

class Body:
    def __init__(self):
        self.legs = {
            "front_left": Leg("front_left", pca),
            "back_left": Leg("back_left", pca),
            "back_right": Leg("back_right", pca),
            "front_right": Leg("front_right", pca),
        }

    def reset(self):
        for leg in self.legs.values():
            leg.reset()

    def up(self):
        for leg in self.legs.values():
            leg.up()

    def down(self):
        for leg in self.legs.values():
            leg.down()