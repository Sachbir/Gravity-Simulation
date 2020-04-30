# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import sqrt
from random import uniform

import config
from Render import Render


class Body:

    radius_size_magnifier = 10
    change_rate = 1.1

    def __init__(self, name, position=None):

        self.name = name
        self.color = 255, 255, 255

        self.mass = 1
        self.velocity = 0, 0

        if position is not None:
            self.position = position
        else:
            self.position = (int(config.window_size[0] * uniform(1/4, 3/4)),
                             int(config.window_size[1] * uniform(1/4, 3/4)))

        self.future_positions = []
        self.future_velocities = []

    @property
    def mass(self):
        return self.__mass

    @mass.setter
    def mass(self, mass):

        if mass < 0:
            return
        self.__mass = mass
        self.radius = (self.mass * Body.radius_size_magnifier) ** (1.0 / 3)

    def update_velocity(self, all_bodies):

        for otherBody in all_bodies:

            if otherBody == self:
                continue

            a = Body.calc_acceleration_due_to_gravity(self.position, otherBody.position, otherBody.mass)
            v = a * config.UPS_max
            self.velocity = Calc.add_vector2(self.velocity, v)

    @staticmethod
    def calc_acceleration_due_to_gravity(self_pos, other_pos, other_mass):

        # F =  dir * G * m1 * m2 / r^2
        # m1 * a = dir * G * m1 * m2 / r^2
        # a = dir * G * m2 / r ^ 2

        direction = Calc.subtract_vector2(other_pos, self_pos)
        direction = Calc.normalize_vector2(direction)

        # r is the distance between the 2 bodies' centers
        r = sqrt((other_pos[0] - self_pos[0]) ** 2 +
                 (other_pos[1] - self_pos[1]) ** 2)

        a = config.gravitational_constant * other_mass / (r ** 2)
        a = Calc.multiply_vector2_by_factor(direction, a)

        # a = v / t
        # v = a * t
        # t = 1/60 (60 ticks/second)

        return a

    def update_position(self):

        self.position = Calc.add_vector2(self.position, self.velocity)

    def render(self):

        Render.draw_circle(self.position, color=self.color, radius=int(self.radius))

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

            a = Body.calc_acceleration_due_to_gravity(self.future_positions[i - 1],
                                                      otherBody.future_positions[i - 1], otherBody.mass)
            v = a * config.UPS_max
            velocity = Calc.add_vector2(velocity, v)

        self.future_velocities.append(velocity)

    def calc_future_position(self, i):

        if i == 0:
            self.future_positions.append(self.position)
        else:
            self.future_positions.append(Calc.add_vector2(self.future_positions[i - 1], self.future_velocities[i]))

    def render_paths(self):

        Render.draw_lines(self.future_positions, color=(55, 55, 55))

    # Methods for externally editing body properties (mass, velocity)

    def mass_inc(self):

        self.mass *= Body.change_rate

    def mass_dec(self):

        if self.mass > 0.1:
            self.mass /= Body.change_rate

    def vel_x_inc(self):

        vel_x = Body.__inc_prop_val(self.velocity[0])
        self.velocity = (vel_x, self.velocity[1])

    def vel_x_dec(self):

        vel_x = Body.__dec_prop_val(self.velocity[0])
        self.velocity = (vel_x, self.velocity[1])

    def vel_y_inc(self):

        vel_y = Body.__inc_prop_val(self.velocity[1])
        self.velocity = (self.velocity[0], vel_y)

    def vel_y_dec(self):

        vel_y = Body.__dec_prop_val(self.velocity[1])
        self.velocity = (self.velocity[0], vel_y)

    @staticmethod
    def __inc_prop_val(x):
        # used by external functions to modify properties (mass and velocity)
        # function to increase values
        # if negative, divide by the change rate (shrink), if positive, multiply by the change rate (grow)
        # if it's a small value, then add so it can cross from negative to positive

        if x > 0.1:
            return x * Body.change_rate
        elif x < -0.1:
            return x / Body.change_rate
        else:
            return x + 0.1

    @staticmethod
    def __dec_prop_val(x):
        # used by external functions to modify properties (mass and velocity)
        # function to decrease values
        # if positive, divide by the change rate (shrink), if negative, multiply by the change rate (grow)
        # if it's a small value, then subtract so it can cross from positive to negative

        if x > 0.1:
            return x / Body.change_rate
        elif x < -0.1:
            return x * Body.change_rate
        else:
            return x - 0.1


class Calc:

    @staticmethod
    def round_tuple(x):

        return round(x[0]), round(x[1])

    @staticmethod
    def add_vector2(a, b):

        return (a[0] + b[0],
                a[1] + b[1])

    @staticmethod
    def subtract_vector2(a, b):

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
    def multiply_vector2_by_factor(vector, factor):

        return (vector[0] * factor,
                vector[1] * factor)
