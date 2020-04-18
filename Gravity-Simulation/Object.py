# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import pi, sqrt
import pygame
from random import uniform

import config


class Object:

    max_mass = 100
    max_density = 100

    def __init__(self, position=None):

        if position is None:
            self.position = (int(uniform(config.window_size[0] / 4, 3 * config.window_size[0] / 4)),
                             int(uniform(config.window_size[0] / 4, 3 * config.window_size[1] / 4)))
        else:
            self.position = position

        # self.mass = uniform(10, Object.max_mass)
        # self.density = uniform(10, Object.max_density)
        self.mass = self.density = 50

        self.radius = 5
        self.calculate_radius()

        self.motion_vector = (uniform(-1, 1),
                              uniform(-1, 1))

        self.collision_box = None

    def calculate(self, objects):

        net_acceleration = 0, 0

        for o in objects:
            vector = self.get_acceleration_vector(o)
            net_acceleration = (net_acceleration[0] + vector[0],
                                net_acceleration[1] + vector[1])

        self.motion_vector = (self.motion_vector[0] + net_acceleration[0],
                              self.motion_vector[1] + net_acceleration[1])

    def update_velocity(self, allBodies):

        for otherBody in allBodies:
            squareDist = 0
            forceDir = Object.normalize_vector(Object.subtract_vectors(otherBody.position, self.position))
            force = forceDir * config.gravitational_constant * self.mass * otherBody.mass / (2 ** 2)

    @staticmethod
    def subtract_vectors(a, b):

        if len(a) != len(b):
            raise ArithmeticError('Cannot subtract 2 tuples of different lengths')

        c = []
        for i in range(len(a)):
            c.append(a[i] - b[i])

        return tuple(c)

    def get_acceleration_vector(self, o):

        # cos(theta) = adj / hyp
        # hyp = sqrt(x^2 + y^2)
        # cos(theta) = y / hyp

        if self == o:
            return 0, 0

        try:
            relative_position = (o.position[0] - self.position[0],
                                    o.position[1] - self.position[1])

            hypotenuse = sqrt(relative_position[0] ** 2 + relative_position[1] ** 2)

            magnitude = self.get_acceleration_due_to_gravity_from(o)

            acceleration_x = magnitude * relative_position[0] / hypotenuse
            acceleration_y = magnitude * relative_position[1] / hypotenuse

            return acceleration_x, acceleration_y

        except ZeroDivisionError:
            return 0, 0

    def update_and_render(self):

        self.position = Object.add_tuple(self.position,
                                         self.motion_vector)

        pygame.draw.circle(pygame.display.get_surface(),
                           self.get_color(),
                           Object.round_tuple(self.position),
                           self.radius)

    def get_color(self):

        # Figure out where this object lies in potential density
        value = self.density / Object.max_density
        # Use that fraction to get how strongly to give it colour
        value = int(255 * value)
        value = 255 - value

        return value, value, value

    def calculate_radius(self):

        volume = self.mass / self.density
        # V = 4 / 3 * pi * r ^ 3
        # r = (V * 3 / 4 / pi) ^ (1/3)
        self.radius = (volume * 3 / 4 / pi) ** (1 / 3)
        self.radius *= 10
        self.radius = int(self.radius)

    @staticmethod
    def add_tuple(a, b):

        return (a[0] + b[0],
                a[1] + b[1])

    @staticmethod
    def round_tuple(x):

        return round(x[0]), round(x[1])

    def get_acceleration_due_to_gravity_from(self, obj):

        #      F1 = G * m1 * m2 / r ** 2
        # m1 * a1 = G * m1 * m2 / r ** 2
        #      a1 = G * m2 / r ** 2

        dist_between = Object.get_distance_between(self.position, obj.position)
        if dist_between > 10 * config.window_size[0]:
            return 0

        acceleration_due_to_gravity = config.gravitational_constant * obj.mass / dist_between ** 2

        return acceleration_due_to_gravity

    def distance_to(self, obj):

        delta_x = obj.position[0] - self.position[0]
        delta_y = obj.position[1] - self.position[1]

        return sqrt(delta_x ** 2 + delta_y ** 2)

    def collides_with(self, obj):

        if self == obj:
            return False

        combined_radius = self.radius + obj.radius
        dist_between = Object.get_distance_between(self.position, obj.position)
        if combined_radius > dist_between:
            return True
        return False

    def check_for_collisions(self, objects):

        for o in objects:
            if self.collides_with(o):
                self.mass += o.mass

                self_weighting = self.mass / (self.mass + o.mass)
                o_weighting = o.mass / (self.mass + o.mass)

                self.motion_vector = (self.motion_vector[0] * self_weighting + o.motion_vector[0] * o_weighting,
                                      self.motion_vector[1] * self_weighting + o.motion_vector[1] * o_weighting)
                self.calculate_radius()
                # objects.remove(o)
                # o.mass = 0
                o.position = (-1000000, -1000000)
                # TODO: replace this lazy solution (moving far away) with actually removing the object
                # o.isDead = True

    @staticmethod
    def get_distance_between(a, b):

        delta_x = b[0] - a[0]
        delta_y = b[1] - a[1]

        return sqrt(delta_x ** 2 + delta_y ** 2)

    @staticmethod
    def normalize_vector(vector):
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
