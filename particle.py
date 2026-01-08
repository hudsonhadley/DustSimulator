from pole import Pole
import math


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, mass: float=5):
        self.x = x
        self.y = y

        self.vx = vx
        self.vy = vy

        self.mass = mass
        self.G = 6.674 # Gravitational constant. This means that mass is in units of 10^11 kg

    def update(self, poles: list[Pole]):
        self.x += self.vx
        self.y += self.vy

        total_ax: float = 0
        total_ay: float = 0

        for pole in poles:
            dist: float = math.sqrt((self.x - pole.x)**2 + (self.y - pole.y)**2)

            dir: float = math.atan2(self.x - pole.x, self.y - pole.y)
            if pole.is_push:
                dir += math.pi

            f: float = self.mass * pole.mass * self.G / (dist * dist)

            fx: float = f * math.cos(dir)
            fy: float = f * math.cos(dir)

            ax: float = fx / self.mass
            ay: float = fy / self.mass

            total_ax += ax
            total_ay += ay

        self.vx += total_ax
        self.vy += total_ay
