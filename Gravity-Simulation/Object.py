# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import pi
import pygame
from random import uniform

import config


class Object:

    max_mass = 100
    max_density = 100

    def __init__(self):

        self.coordinates = (int(uniform(0, config.window_size[0])),
                            int(uniform(0, config.window_size[1])))

        self.mass = uniform(0, Object.max_mass)
        self.density = uniform(0, Object.max_density)

        # volume = mass / density
        volume = self.mass / self.density
        # V = 4 / 3 * pi * r ^ 3
        # r = (V * 3 / 4 / pi) ^ (1/3)
        self.radius = (volume * 3 / 4 / pi) ** (1 / 3)
        self.radius *= 10
        self.radius = int(self.radius)

    def update(self):

        pass

    def render(self):

        pygame.draw.circle(pygame.display.get_surface(),
                           self.get_color(),
                           self.coordinates,
                           self.radius)

    def get_color(self):

        # Figure out where this object lies in potential density
        value = self.density / Object.max_density
        # Use that fraction to get how strongly to give it colour
        value = int(255 * value)

        return value, value, value
