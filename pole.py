class Pole:
    def __init__(self, x: float, y: float, is_push: bool, mass: float=5):
        self.x = x
        self.y = y

        self.is_push = is_push
        self.mass = mass
