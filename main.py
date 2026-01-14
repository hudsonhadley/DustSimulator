from typing import Any
import pygame

from particle import Particle
from pole import Pole
from random import randint
import json
import math

def generate_donut(particle_list: list[Particle], x: int, y: int, particle_count: int, radius: int, width: int, speed: int=0):
    for i in range(particle_count):
        mag = randint(radius-width, radius)    
        dir = math.radians(randint(0, 360))

        x_pos = mag * math.cos(dir) + x
        y_pos = mag * math.sin(dir) + y

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

def read_scenario(scenario_file: str) -> dict[str, Any]:
    """
    Expects a scenario filename. The contents should be a json that can include screen size, 
    background color, particle color option, particle placement, and pole placement. The
    returning dictionary will include the screensize, background color, particle color
    option, list of particles, and list of poles. 
    """

    with open(scenario_file, 'rt', encoding='utf-8') as scen_in:
        scenario: dict[str, Any] = json.load(scen_in)

    parsed_scenario: dict[str, Any] = dict()

    parsed_scenario["width"] = scenario.get("width", 1000)
    parsed_scenario["height"] = scenario.get("height", 1000)
    parsed_scenario["background_color"] = scenario.get("background_color", [0, 0, 0])
    parsed_scenario["particle_color"] = scenario.get("particle_color", [255, 255, 255])

    parsed_scenario["particles"] = []
    for particle_spec in scenario["particles"]:
        if particle_spec["shape"] == "donut":
            generate_donut(parsed_scenario["particles"],
                           particle_spec["x"],
                           particle_spec["y"],
                           particle_spec["count"],
                           particle_spec["radius"],
                           particle_spec["width"],
                           particle_spec.get("speed", 0)
                           )
        elif particle_spec["shape"] == "circle":
            generate_circle(parsed_scenario["particles"],
                            particle_spec["count"],
                            particle_spec["x"],
                            particle_spec["y"],
                            particle_spec["radius"],
                            particle_spec.get("vx", 0),
                            particle_spec.get("vy", 0)
                            )
    
    parsed_scenario["poles"] = []
    
    return parsed_scenario


def main():
    pygame.init()
    scenario_mapping = read_scenario("scenario.json")
    width = scenario_mapping["width"]
    height = scenario_mapping["height"]
    
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True

    push_pole_color: tuple[int, int, int] = (0, 0, 255)
    pull_pole_color: tuple[int, int, int] = (255, 0, 0)
    pole_size: int = 8

    particle_size: int = 1

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for particle in scenario_mapping["particles"]:
            net_force = pygame.Vector2(0, 0)
            for pole in scenario_mapping["poles"]:
                net_force += pole.force_on(particle)

            particle.apply_force(net_force, dt)
            particle.update(dt)

        for pole in scenario_mapping["poles"]:
            pole.move(dt)

        screen.fill(scenario_mapping["background_color"])

        # Draw poles
        for pole in scenario_mapping["poles"]:
            if pole.strength < 0:
                pygame.draw.circle(screen, push_pole_color, pole.pos, pole_size)
            else:
                pygame.draw.circle(screen, pull_pole_color, pole.pos, pole_size)

        # Draw particles
        for particle in scenario_mapping["particles"]:
            if scenario_mapping["particle_color"] == "direction":
                pygame.draw.circle(screen, particle.get_color_from_direction(), particle.pos, particle_size)
            elif scenario_mapping["particle_color"] == "magnitude":
                pygame.draw.circle(screen, particle.get_color_from_velocity(), particle.pos, particle_size)
            else:
                pygame.draw.circle(screen, scenario_mapping["particle_color"], particle.pos, particle_size)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()

if __name__ == '__main__':
    main()


