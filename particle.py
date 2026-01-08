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
