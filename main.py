import pygame

from particle import Particle
from pole import Pole
from random import randint
    

def main():
    pygame.init()
    width = 1000
    height = 1000
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True
    particle_count = 2000

    particles: list[Particle] = []
    for i in range(particle_count):
        particles.append(Particle(randint(0, 250), randint(0, 250), vx=150))
    
    poles: list[Pole] = [
                         Pole(450, 450, -100),
                         Pole(450, 500, 100),
                         Pole(450, 550, -100),
                         Pole(500, 450, 100),
                         Pole(500, 500, 100),
                         Pole(500, 550, 100),
                         Pole(550, 450, -100),
                         Pole(550, 500, 100),
                         Pole(550, 550, -100)
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


