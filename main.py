from typing import Any
import pygame

from random import randint
from make_color_table import read_table
import json
import math
import numpy as np

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

        x_pos = mag * np.cos(dir) + x
        y_pos = mag * np.sin(dir) + y
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
    color_table_file = scenario.get("color_table", None)

    if type(parsed_scenario["particle_color"]) is not list and color_table_file is None:
        raise AttributeError("if a non constant color is defined for the particles, a color table must be provided")
    elif color_table_file is not None:
        parsed_scenario['color_table'] = read_table(color_table_file)

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
    pole_vel = []
    pole_movement = []
    pole_center = []
    pole_count = 0
    for pole_spec in scenario["poles"]:

        if "radius" in pole_spec.keys() and "speed" in pole_spec.keys():
            pole_movement.append('circle')
            theta = np.deg2rad(pole_spec.get('theta', 0))
            pole_vel.append([pole_spec['speed'] * np.sin(theta),
                        pole_spec['speed'] * np.cos(theta)])

            pole_pos.append([
                pole_spec['x'] + pole_spec['radius'] * np.cos(theta),
                pole_spec['y'] + pole_spec['radius'] * np.sin(theta)
            ])

            pole_center.append([pole_spec['x'], pole_spec['y']])

        else:
            pole_movement.append('line')
            pole_vel.append([pole_spec.get('vx', 0), pole_spec.get('vy', 0)])

            pole_pos.append([pole_spec['x'], pole_spec['y']])

            pole_center.append(None)

        pole_strength.append(pole_spec['strength'])
        pole_count += 1

    parsed_scenario['poles'] = {
        'pos': np.array(pole_pos),
        'strength': np.array(pole_strength),
        'vel': np.array(pole_vel),
        'movement': pole_movement,
        'center': pole_center
    }     
    parsed_scenario['pole_count'] = pole_count
    
    return parsed_scenario

def move_particles(particles, poles, dt, force_multiplier=500000):
    if len(particles['pos']) == 0:
        return

    delta = particles["pos"][:, None, :] - poles["pos"][None, :, :]
    dist_sq = np.sum(delta**2, axis=2)
    dist = np.sqrt(dist_sq)

    force_mag = poles["strength"] / dist_sq
    force_dir = delta / dist[:, :, None]
    forces = force_dir * force_mag[:, :, None]

    total_force = force_multiplier * forces.sum(axis=1)

    acc = total_force / particles["mass"][:, None]
    particles['vel'] += acc * dt
    particles['pos'] += particles['vel'] * dt

def move_poles(poles, dt):
    for i in range(len(poles['pos'])):
        if poles['movement'][i] == 'line':
            poles['pos'][i, 0] += poles['vel'][i, 0] * dt
            poles['pos'][i, 1] += poles['vel'][i, 1] * dt
        
        elif poles['movement'][i] == 'circle':
            speed = np.sqrt(poles['vel'][i, 0]**2 + poles['vel'][i, 1]**2)

            r_vec = poles['pos'][i] - poles['center'][i]

            radius = np.sqrt(np.sum((r_vec)**2))

            omega = speed / radius
            dtheta = omega * dt

            rot = np.array([
                [np.cos(dtheta), -np.sin(dtheta)],
                [np.sin(dtheta), np.cos(dtheta)]
            ])

            new_r_vec = np.matmul(rot, r_vec)
            
            poles['pos'][i] = poles['center'][i] + new_r_vec


def main():
    pygame.init()
    scenario_mapping = read_scenario("scenario.json")
    width = scenario_mapping["width"]
    height = scenario_mapping["height"]
    particle_count = scenario_mapping['particle_count']
    pole_count = scenario_mapping['pole_count']
    background_color = scenario_mapping['background_color']
    color_table = scenario_mapping['color_table']

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
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        move_particles(particles, poles, dt)
        move_poles(poles, dt)

        if len(particles['pos']) > 0:
            magnitude = np.sqrt(np.sum(particles['vel']**2, axis=1)) + 1e-8
            direction = np.arctan2(particles['vel'][:, 1], particles['vel'][:, 0])

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
                m = magnitude[i]
                m = m if m <= 360 else 360 # Clamp to be less than or equal to 360

                color_idx = int(m * len(color_table) / 360) % len(color_table)
                pygame.draw.circle(screen, color_table[color_idx], particles['pos'][i], particle_size)

            elif scenario_mapping['particle_color'] == 'direction':
                d = direction[i] * 360 / (2 * np.pi)
                color_idx = int(d * len(color_table) / 360) % len(color_table)
                pygame.draw.circle(screen, color_table[color_idx], particles['pos'][i], particle_size)

            else:
                pygame.draw.circle(screen, scenario_mapping['particle_color'], particles['pos'][i], particle_size)
                
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()

if __name__ == '__main__':
    main()


