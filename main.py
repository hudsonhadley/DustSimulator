import pygame

from particle import Particle
from pole import Pole
from random import randint
import math

def generate_donut(screen_width: int, screen_height: int, particle_list: list[Particle], particle_count: int, radius: int, width: int, speed: int=0):
    for i in range(particle_count):
        mag = randint(radius-width, radius)    
        dir = math.radians(randint(0, 360))

        x = mag * math.cos(dir) + screen_width/2
        y = mag * math.sin(dir) + screen_height/2

        vx = speed * math.cos(dir + math.pi/2)
        vy = speed * math.sin(dir + math.pi/2)
        particle_list.append(Particle(x, y, vx, vy))

def generate_circle(particle_list: list[Particle], particle_count: int, x: int, y: int, radius: int, vx: int=0, vy: int=0):
    for i in range(particle_count):
        mag = randint(0, radius)
        dir = math.radians(randint(0, 360))

        x_pos = mag * math.cos(dir) + x
        y_pos = mag * math.sin(dir) + y

        particle_list.append(Particle(x_pos, y_pos, vx, vy))


def main():
    pygame.init()
    width = 1000
    height = 1000
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True
    particle_count = 4000

    particles: list[Particle] = []
    generate_circle(particles, particle_count, 250, 750, 50, 100)

    poles: list[Pole] = [
                         Pole(500, 500, 100)
                         ]

    push_pole_color: tuple[int, int, int] = (0, 0, 255)
    pull_pole_color: tuple[int, int, int] = (255, 0, 0)
    pole_size: int = 8

    particle_color: tuple[int, int, int] = (255, 255, 255)
    particle_size: int = 3

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for particle in particles:
            net_force = pygame.Vector2(0, 0)
            for pole in poles:
                net_force += pole.force_on(particle)

            particle.apply_force(net_force, dt)
            particle.update(dt)

        screen.fill("black")

        # Draw poles
        for pole in poles:
            if pole.strength < 0:
                pygame.draw.circle(screen, push_pole_color, pole.pos, pole_size)
            else:
                pygame.draw.circle(screen, pull_pole_color, pole.pos, pole_size)

        # Draw particles
        for particle in particles:
            pygame.draw.circle(screen, particle_color, particle.pos, particle_size)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()

if __name__ == '__main__':
    main()


