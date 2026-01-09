import math
import pygame


class Particle :
    def __init__(self, x: float, y: float, vx: float=0, vy: float=0, mass: float=20):
        self.pos: pygame.Vector2 = pygame.Vector2(x, y)
        self.vel: pygame.Vector2 = pygame.Vector2(vx, vy)

        self.mass = mass
        self.G = 6.674 # Gravitational constant. This means that mass is in units of 10^11 kg

    def apply_force(self, force: pygame.Vector2, dt: float):
        self.vel += (force / self.mass) * dt

    def update(self, dt: float):
        self.pos += self.vel * dt

    def get_color_from_velocity(self) -> tuple[int, int, int]:

        # We'll use magnitude as the hue for hsb coloring and then convert to rgb
        magnitude: int = int(self.vel.magnitude())
        if magnitude > 360:
            magnitude = 360

        saturation: float = 1
        brightness: float = 1

        return hsv_to_rgb(magnitude, saturation, brightness)

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h %= 360

    chroma: float = v * s

    X: float = chroma * (1 - abs((h / 60) % 2 - 1))
    m: float = v - chroma

    if h < 60:
        r, g, b = (chroma, X, 0)
    elif h < 120:
        r, g, b = (X, chroma, 0)
    elif h < 180:
        r, g, b = (0, chroma, X)
    elif h < 240:
        r, g, b = (0, X, chroma)
    elif h < 300:
        r, g, b = (X, 0, chroma)
    else:
        r, g, b = (chroma, 0, X)

    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))
        