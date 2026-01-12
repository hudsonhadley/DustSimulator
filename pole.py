from particle import Particle
import pygame
import math

class Pole:
    def __init__(self, x: float, y: float, strength: float, radius: int|None=None, speed: int|None=None, direction: int|None=None, theta_init: int|None=None):
        """
        Positive values pull particles while negative values push them.
        Radius and speed should be assigned when wanting to put the pole on a circular path and the x,y given.
        Speed and direction should be assigned when wanting to put the pole on a direct linear path from the x,y given.
        """
        self.pos: pygame.Vector2 = pygame.Vector2(x, y)
        self.strength = strength # positive = pull, negative = push

        # No path
        if radius is None and speed is None and direction is None:
            self.movement = None

        # Circuit
        elif radius is not None and speed is not None and direction is None:
            self.movement = "Circuit"
            self.center = pygame.Vector2(x, y)
            self.radius = radius
            self.speed = speed

            if theta_init is None:
                theta_init = 0
            
            rad = math.radians(theta_init)
            self.pos.x = self.center.x + self.radius * math.cos(rad)
            self.pos.y = self.center.y + self.radius * math.sin(rad)

        # Line
        elif radius is None and speed is not None and direction is not None:
            self.movement = "Line"
            rad = math.radians(direction)

            vx = speed * math.cos(rad)
            vy = speed * math.sin(rad)

            self.vel = pygame.Vector2(vx, vy)

    def force_on(self, particle: Particle) -> pygame.Vector2:
        direction: pygame.Vector2 = self.pos - particle.pos

        distance = direction.length()

        if distance < 5:
            return pygame.Vector2(0, 0)
        
        direction.normalize_ip()
        FORCE_SCALE = 2000000
        magnitude: float = FORCE_SCALE * self.strength / (distance * distance)
        return direction * magnitude
    
    def move(self, dt: float):
        if self.movement is None:
            return
        elif self.movement == "Circuit":
            theta = math.atan2(self.pos.y - self.center.y, self.pos.x - self.center.x)
            theta += self.speed * dt / self.radius

            self.pos.x = self.center.x + self.radius * math.cos(theta)
            self.pos.y = self.center.y + self.radius * math.sin(theta)
        
        elif self.movement == "Line":
            self.pos += self.vel * dt
