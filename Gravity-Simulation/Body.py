# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import sqrt, ceil
from random import uniform

import config
from Render import Render
from Mutability import Mutability


class Body:

    body_count = 0

    radius_size_magnifier = 10
    change_rate = 1.1
    min_vel = 0.1

    click_precision = 5

    path_color_collision = 110, 55, 55
    selection_color = 165, 55, 55

    ui_properties = [["name", Mutability.STR],
                     ["velocity_x", Mutability.NUM],
                     ["velocity_y", Mutability.NUM],
                     ["mass", Mutability.NUM],
                     ["radius", Mutability.NONE]]

    def __init__(self, position, name=None, mass=1, velocity=(0, 0), colour=None):

        if name is not None:
            self.name = name
        else:
            self.name = "Body_" + str(Body.body_count)
        Body.body_count += 1

        # if position is not None:
        self.position = position
        # else:
        #     self.position = (int(config.window_size[0] * uniform(1/4, 3/4)),
        #                      int(config.window_size[1] * uniform(1/4, 3/4)))
        self.mass = mass
        self.velocity = velocity
        if colour is not None:
            self.colour = colour
        else:
            self.colour = Body.generate_pastel_colour()
        self.path_colour_default = Body.generate_path_colour(self.colour)
        self.path_colour = self.path_colour_default

        self.future_positions = []
        self.future_velocities = []

    @staticmethod
    def generate_pastel_colour():

        r = uniform(127, 255)
        g = uniform(127, 255)
        b = uniform(127, 255)

        return r, g, b

    @staticmethod
    def generate_path_colour(colour):

        r = int(colour[0] / 2)
        g = int(colour[1] / 2)
        b = int(colour[2] / 2)

        return r, g, b

    @property
    def mass(self):
        return self.__mass

    @mass.setter
    def mass(self, mass):

        if mass < 0:
            return
        self.__mass = mass
        self.radius = (self.mass * Body.radius_size_magnifier) ** (1.0 / 3)

    @property
    def velocity_x(self):
        return self.velocity[0]

    @velocity_x.setter
    def velocity_x(self, velocity_x):

        self.velocity = velocity_x, self.velocity[1]

    @property
    def velocity_y(self):
        return self.velocity[1]

    @velocity_y.setter
    def velocity_y(self, velocity_y):

        self.velocity = self.velocity[0], velocity_y

    def render(self):

        Render.draw_circle(self.position, colour=self.colour, radius=int(self.radius))

    def render_select_bubble(self):

        border = int(0.1 * self.radius + 1)

        Render.draw_circle(self.position, colour=Body.selection_color, radius=int(self.radius + 1), border=border)

    def update_position(self):

        self.position = Calc.add_vector2(self.position, self.velocity)

    def update_velocity(self, all_bodies):

        for otherBody in all_bodies:

            if otherBody == self:
                continue

            a = self.calc_acceleration_due_to_gravity(self.position, otherBody.position, otherBody.mass)
            # a = v / t
            # v = a * t
            # t = 1/60 (60 ticks/second)
            v = a * int(config.UPS)
            self.velocity = Calc.add_vector2(self.velocity, v)

    def calc_acceleration_due_to_gravity(self, self_pos, other_pos, other_mass):

        # F =  dir * G * m1 * m2 / r^2
        # m1 * a = dir * G * m1 * m2 / r^2
        # a = dir * G * m2 / r ^ 2

        direction = Calc.subtract_vector2(other_pos, self_pos)
        direction = Calc.normalize_vector2(direction)

        # r is the distance between the 2 bodies' centers
        r = sqrt((other_pos[0] - self_pos[0]) ** 2 +
                 (other_pos[1] - self_pos[1]) ** 2)

        if r < 10:
            self.path_colour = Body.path_color_collision

        a = config.gravitational_constant * other_mass / (r ** 2)
        a = Calc.multiply_vector2_by_factor(direction, a)

        return a

    def center_values_on_focus_body(self, focus_body):

        self.velocity = Calc.subtract_vector2(self.velocity, focus_body.velocity)
        self.position = Calc.subtract_vector2(self.position, focus_body.position)

    def click_point(self, point):

        x_sq = (point[0] - self.position[0]) ** 2
        y_sq = (point[1] - self.position[1]) ** 2

        dist = sqrt(x_sq + y_sq)

        return dist < (self.radius + Body.click_precision)

    # Methods for predicting the future path of the body

    def render_paths(self):

        path_width = ceil(self.radius / 4)

        Render.draw_lines(self.future_positions, color=self.path_colour, width=path_width)

    def prediction_velocities(self, all_bodies, i):

        if i == 0:
            self.future_velocities.append(self.velocity)
            return

        velocity = self.future_velocities[i - 1]

        for otherBody in all_bodies:

            if otherBody == self:
                continue

            a = self.calc_acceleration_due_to_gravity(self.future_positions[i - 1],
                                                      otherBody.future_positions[i - 1], otherBody.mass)
            # a = v / t
            # v = a * t
            # t = 1/60 (60 ticks/second)
            v = a * config.UPS
            velocity = Calc.add_vector2(velocity, v)

        self.future_velocities.append(velocity)

    def prediction_positions(self, i):

        if i == 0:
            self.future_positions.append(self.position)
        else:
            self.future_positions.append(Calc.add_vector2(self.future_positions[i - 1], self.future_velocities[i]))

    def predictions_reset(self):

        self.future_velocities = []
        self.future_positions = []
        self.path_colour = self.path_colour_default

    def predictions_center_on_focus_body(self, focus_body):

        for i in range(len(self.future_positions)):
            future_offset = Calc.subtract_vector2(Render.offset,
                                                  Render.calc_offset(focus_body.future_positions[i]))

            self.future_positions[i] = Calc.subtract_vector2(self.future_positions[i],
                                                             future_offset)

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

        if x >= Body.min_vel:
            return x * Body.change_rate
        elif x < -Body.min_vel:
            return x / Body.change_rate
        else:
            return x + Body.min_vel

    @staticmethod
    def __dec_prop_val(x):
        # used by external functions to modify properties (mass and velocity)
        # function to decrease values
        # if positive, divide by the change rate (shrink), if negative, multiply by the change rate (grow)
        # if it's a small value, then subtract so it can cross from positive to negative

        if x > Body.min_vel:
            return x / Body.change_rate
        elif x <= -Body.min_vel:
            return x * Body.change_rate
        else:
            return x - Body.min_vel


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
