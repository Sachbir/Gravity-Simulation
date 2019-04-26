# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import pi, sqrt
import pygame
from random import uniform

import config


class Object:

    max_mass = 100
    max_density = 100

    def __init__(self):

        self.coordinates = (int(uniform(0, config.window_size[0])),
                            int(uniform(0, config.window_size[1])))

        # self.mass = uniform(0, Object.max_mass)
        # self.density = uniform(0, Object.max_density)

        self.mass = self.density = 50

        # volume = mass / density
        volume = self.mass / self.density
        # V = 4 / 3 * pi * r ^ 3
        # r = (V * 3 / 4 / pi) ^ (1/3)
        self.radius = (volume * 3 / 4 / pi) ** (1 / 3)
        self.radius *= 10
        self.radius = int(self.radius)

        self.motion_vector = (uniform(-1, 1),
                              uniform(-1, 1))

    def calculate(self, objects):

        # Simplifying down to a 2-body system first

        other_object = objects[0]
        if other_object == self:
            other_object = objects[1]

        dist_between_objects = self.distance_to(other_object)

        g_force = config.gravitational_constant * self.mass * other_object.mass / dist_between_objects ** 2
        acceleration = g_force / self.mass

        vector_to_other_object = (other_object.coordinates[0] - self.coordinates[0],
                                  other_object.coordinates[1] - self.coordinates[1])
        vector_to_other_object = Object.get_unit_vector(vector_to_other_object)

        pygame.draw.line(pygame.display.get_surface(),
                         (255, 255, 255),
                         Object.round_tuple(self.coordinates),
                         Object.round_tuple(Object.add_tuple(self.coordinates, vector_to_other_object)))

        vector_from_gravity = Object.scale_vector(vector_to_other_object, acceleration)

        # vector_from_gravity = map(lambda x: x * config.gravitational_constant, vector_to_other_object)

        self.motion_vector = Object.add_tuple(self.motion_vector,
                                              vector_from_gravity)

    def update_and_render(self):

        self.coordinates = Object.add_tuple(self.coordinates,
                                            self.motion_vector)

        pygame.draw.circle(pygame.display.get_surface(),
                           self.get_color(),
                           Object.round_tuple(self.coordinates),
                           self.radius)

    def get_color(self):

        # Figure out where this object lies in potential density
        value = self.density / Object.max_density
        # Use that fraction to get how strongly to give it colour
        value = int(255 * value)
        value = 255 - value

        return value, value, value

    @staticmethod
    def add_tuple(a, b):

        return (a[0] + b[0],
                a[1] + b[1])

    @staticmethod
    def round_tuple(x):

        return round(x[0]), round(x[1])

    # for 2-body system
    def get_acceleration_due_to_gravity_from(self, total_mass):

        # F = G * m1 * m2 / r ** 2

        dist_between = Object.get_distance_between(self.coordinates, total_mass.coordinates)

        acceleration_due_to_gravity = config.gravitational_constant * total_mass.mass / self.mass / dist_between ** 2

        return acceleration_due_to_gravity

    def distance_to(self, obj):

        delta_x = obj.coordinates[0] - self.coordinates[0]
        delta_y = obj.coordinates[1] - self.coordinates[1]

        return sqrt(delta_x ** 2 + delta_y ** 2)

    @staticmethod
    def get_distance_between(a, b):

        delta_x = b[0] - a[0]
        delta_y = b[1] - a[1]

        return sqrt(delta_x ** 2 + delta_y ** 2)

    @staticmethod
    def get_unit_vector(vector):
        """Takes a given vector and normalizes it to a magnitude of 1"""

        vector_magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2)

        if vector_magnitude == 0:
            return 0, 0

        unit_vector = (vector[0] / vector_magnitude,
                       vector[1] / vector_magnitude)
        return unit_vector

    @staticmethod
    def scale_vector(vector, acceleration):

        x = vector[0] * acceleration
        y = vector[1] * acceleration

        return x, y
