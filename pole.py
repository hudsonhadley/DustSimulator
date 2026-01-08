from particle import Particle
import pygame

class Pole:
    def __init__(self, x: float, y: float, strength: float):
        self.pos: pygame.Vector2 = pygame.Vector2(x, y)
        self.strength = strength # positive = pull, negative = push

    def force_on(self, particle: Particle) -> pygame.Vector2:
        direction: pygame.Vector2 = self.pos - particle.pos

        distance = direction.length()

        if distance < 5:
            return pygame.Vector2(0, 0)
        
        direction.normalize_ip()
        FORCE_SCALE = 2000000
        magnitude: float = FORCE_SCALE * self.strength / (distance * distance)
        return direction * magnitude