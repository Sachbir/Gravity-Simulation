# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import pi, sqrt
import pygame
from random import uniform

import config
from Render import Render


class Body:

    min_color = 100
    max_color = 255

    def __init__(self, position=None):

        self.color = 255, 255, 255
        # self.color = 0, 0, 0

        self.mass = int(uniform(1, 5))
        self.radius = 4
        self.velocity = (uniform(-2, 2),
                         uniform(-2, 2))
        self.velocity = 0, 0

        if position is not None:
            self.position = position
        else:
            self.position = (int(config.window_size[0] * uniform(1/4, 3/4)),
                             int(config.window_size[1] * uniform(1/4, 3/4)))

        self.future_positions = []
        self.future_velocities = []

    def update_velocity(self, all_bodies):

        for otherBody in all_bodies:

            if otherBody == self:
                continue

            # F =  dir * G * m1 * m2 / r^2
            # m1 * a = dir * G * m1 * m2 / r^2
            # a = dir * G * m2 / r ^ 2

            direction = Calc.sub_vector2(otherBody.position, self.position)
            direction = Calc.normalize_vector2(direction)

            a = config.gravitational_constant * otherBody.mass / (otherBody.radius ** 2)
            a = Calc.mul_vector2_by_factor(direction, a)

            # a = v / t
            # v = a * t
            # t = 1/60 (60 ticks/second)

            v = a * config.UPS_max

            self.velocity = Calc.add_vector2(self.velocity, v)

    def update_position(self):

        self.position = Calc.add_vector2(self.position, self.velocity)

    def render(self):

        Render.draw_circle(self.position, color=self.color, radius=self.radius)

    def collide_point(self, point):

        x_sq = (point[0] - self.position[0]) ** 2
        y_sq = (point[1] - self.position[1]) ** 2

        dist = sqrt(x_sq + y_sq)

        return dist < self.radius

    def get_offset_to_center_this(self):

        x = self.position[0] - config.window_size[0] / 2
        y = self.position[1] - config.window_size[1] / 2

        return x, y

    def calc_future_velocity(self, all_bodies, i):

        if i == 0:
            self.future_velocities.append(self.velocity)
            return

        velocity = self.future_velocities[i - 1]

        for otherBody in all_bodies:

            if otherBody == self:
                continue

            # F =  dir * G * m1 * m2 / r^2
            # m1 * a = dir * G * m1 * m2 / r^2
            # a = dir * G * m2 / r ^ 2

            direction = Calc.sub_vector2(otherBody.future_positions[i - 1], self.future_positions[i - 1])

            direction = Calc.normalize_vector2(direction)

            a = config.gravitational_constant * otherBody.mass / (otherBody.radius ** 2)
            a = Calc.mul_vector2_by_factor(direction, a)

            # a = v / t
            # v = a * t
            # t = 1/60 (60 ticks/second)

            v = a * config.UPS_max

            velocity = Calc.add_vector2(velocity, v)

        self.future_velocities.append(velocity)

    def calc_future_position(self, i):

        if i == 0:
            self.future_positions.append(self.position)
        else:
            self.future_positions.append(Calc.add_vector2(self.future_positions[i - 1], self.future_velocities[i]))

    def render_paths(self):

        Render.draw_lines(self.future_positions, color=(255, 255, 255))


class Calc:

    @staticmethod
    def round_tuple(x):

        return round(x[0]), round(x[1])

    @staticmethod
    def add_vector2(a, b):

        return (a[0] + b[0],
                a[1] + b[1])

    @staticmethod
    def sub_vector2(a, b):

        return (a[0] - b[0],
                a[1] - b[1])

    @staticmethod
    def normalize_vector2(vector):
        """Takes a given vector and normalizes it to a magnitude of 1"""

        vector_magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2)

        if vector_magnitude == 0:
            return 0, 0

        unit_vector = (vector[0] / vector_magnitude,
                       vector[1] / vector_magnitude)
        return unit_vector

    @staticmethod
    def mul_vector2_by_factor(vector, factor):

        return (vector[0] * factor,
                vector[1] * factor)
