from typing import Any
import pygame

from random import randint
import json
import math
import numpy as np

def get_color_from_magnitude(vel: list[float]) -> tuple[int, int, int]:

        # We'll use magnitude as the hue for hsv coloring and then convert to rgb
        magnitude = math.sqrt(vel[0]*vel[0] + vel[1]*vel[1])
        if magnitude > 360:
            magnitude = 360

        saturation: float = 1
        brightness: float = 1

        return hsv_to_rgb(magnitude, saturation, brightness)
    
def get_color_from_direction(vel: list[float]) -> tuple[int, int, int]:
    # Use direction of velovity for hsv coloring and then convert to rgb

    direction = math.atan2(vel[1], vel[0])

    saturation = 1
    brightness = 1

    return hsv_to_rgb(direction, saturation, brightness)

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

def generate_donut(particle_pos: list[list[float]], 
                   particle_vel: list[list[float]],
                   particle_count: int,
                   x: float, 
                   y: float,
                   radius: int,
                   width: int, 
                   speed: float=0
                   ):
    
    for i in range(particle_count):
        mag = randint(radius-width, radius)    
        dir = math.radians(randint(0, 360))

        x_pos = mag * math.cos(dir) + x
        y_pos = mag * math.sin(dir) + y
        particle_pos.append([x_pos, y_pos])

        vx = speed * math.cos(dir + math.pi/2)
        vy = speed * math.sin(dir + math.pi/2)
        particle_vel.append([vx, vy])

def generate_circle(particle_pos: list[list[float]], 
                    particle_vel: list[list[float]], 
                    particle_count: int, 
                    x: float, 
                    y: float, 
                    radius: int, 
                    vx: float=0, 
                    vy: float=0):
    
    for i in range(particle_count):
        mag = randint(0, radius)
        dir = math.radians(randint(0, 360))

        x_pos = mag * math.cos(dir) + x
        y_pos = mag * math.sin(dir) + y
        particle_pos.append([x_pos, y_pos])
        particle_vel.append([vx, vy])

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

    particle_pos = []
    particle_vel = []

    total_particle_count = 0
    for particle_spec in scenario["particles"]:
        if particle_spec["shape"] == "donut":
            generate_donut(particle_pos,
                           particle_vel,
                           particle_spec["count"],
                           particle_spec["x"],
                           particle_spec["y"],
                           particle_spec["radius"],
                           particle_spec["width"],
                           particle_spec.get("speed", 0)
                           )
            
        elif particle_spec["shape"] == "circle":
            generate_circle(particle_pos,
                            particle_vel,
                            particle_spec["count"],
                            particle_spec["x"],
                            particle_spec["y"],
                            particle_spec["radius"],
                            float(particle_spec.get("vx", 0)),
                            float(particle_spec.get("vy", 0))
                            )
            
        total_particle_count += particle_spec['count']
    
    parsed_scenario['particles'] = {
        'pos': np.array(particle_pos),
        'vel': np.array(particle_vel),
        'mass': np.full(total_particle_count, scenario['mass'])
    }
    parsed_scenario['particle_count'] = total_particle_count
    
    pole_pos = []
    pole_strength = []
    pole_count = 0
    for pole_spec in scenario["poles"]:
        pole_pos.append([pole_spec['x'], pole_spec['y']])
        pole_strength.append(pole_spec['strength'])

        pole_count += 1

    parsed_scenario['poles'] = {
        'pos': np.array(pole_pos),
        'strength': np.array(pole_strength)
    }     
    parsed_scenario['pole_count'] = pole_count
    
    return parsed_scenario


def main():
    pygame.init()
    scenario_mapping = read_scenario("scenario.json")
    width = scenario_mapping["width"]
    height = scenario_mapping["height"]
    particle_count = scenario_mapping['particle_count']
    pole_count = scenario_mapping['pole_count']
    background_color = scenario_mapping['background_color']

    particles = scenario_mapping['particles']
    poles = scenario_mapping['poles']
    
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True

    push_pole_color: tuple[int, int, int] = (100, 100, 255)
    pull_pole_color: tuple[int, int, int] = (255, 0, 0)
    pole_size: int = 8

    particle_size: int = 1

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        delta = particles["pos"][:, None, :] - poles["pos"][None, :, :]
        dist_sq = np.sum(delta**2, axis=2)
        dist = np.sqrt(dist_sq)

        force_mag = poles["strength"] / dist_sq
        force_dir = delta / dist[:, :, None]
        forces = force_dir * force_mag[:, :, None]

        total_force = forces.sum(axis=1)

        acc = total_force / particles["mass"][:, None]
        particles['vel'] += acc * dt
        particles['pos'] += particles['vel'] * dt

        screen.fill(background_color)

        # Draw poles
        for i in range(pole_count):

            if poles['strength'][i] > 0:
                pygame.draw.circle(screen, push_pole_color, poles['pos'][i], pole_size)
            else:
                pygame.draw.circle(screen, pull_pole_color, poles['pos'][i], pole_size)

        # Draw particles
        for i in range(particle_count):
            if scenario_mapping['particle_color'] == 'magnitude':
                pygame.draw.circle(screen, get_color_from_magnitude(particles['vel'][i]), particles['pos'][i], particle_size)
            elif scenario_mapping['particle_color'] == 'direction':
                pygame.draw.circle(screen, get_color_from_direction(particles['vel'][i]), particles['pos'][i], particle_size)
            else:
                pygame.draw.circle(screen, scenario_mapping['particle_color'], particles['pos'][i], particle_size)
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()

if __name__ == '__main__':
    main()


