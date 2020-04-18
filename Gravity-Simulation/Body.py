# Math is done as if these are 3D objects operating on a 2D plane, as gravity does not work in 2 dimensions

from math import pi, sqrt
import pygame
from random import uniform

import config
from Render import Render


class Body:

    def __init__(self, position=None):

        self.color = 255, 255, 255

        self.mass = 0
        self.radius = 4
        self.velocity = (uniform(-2, 2),
                         uniform(-2, 2))

        if position is not None:
            self.position = position
        else:
            self.position = (int(uniform(Render.screen_left / 2, Render.screen_right / 2)),
                             int(uniform(Render.screen_top / 2, Render.screen_bottom / 2)))

    def update_velocity(self):

        pass

    def update_position(self):

        self.position = Calc.add_vector2(self.position, self.velocity)

    def render(self):

        Render.draw_circle(self.position, color=(255, 255, 255))

    def get_color(self):

        return self.color


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
