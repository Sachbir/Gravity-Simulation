import pygame
from copy import deepcopy


class Render:

    width = 0
    height = 0

    screen_top = 0
    screen_bottom = 0
    screen_left = 0
    screen_right = 0

    offset = 0, 0

    @staticmethod
    def set_surface(surface):

        Render.width, Render.height = surface.get_size()

        Render.screen_top = 0
        Render.screen_bottom = Render.height
        Render.screen_left = 0
        Render.screen_right = Render.width

        Render.offset = 0, 0

    @staticmethod
    def convert_to_pygame(point):

        x = point[0] + Render.offset[0]
        y = point[1] + Render.offset[1]

        return int(x), int(y)

    @staticmethod
    def convert_to_renderer(point):

        x = point[0] - Render.offset[0]
        y = point[1] - Render.offset[1]

        return int(x), int(y)

    @staticmethod
    def draw_circle(position, radius=5, color=(0, 0, 0), border=0):

        pygame.draw.circle(pygame.display.get_surface(), color, Render.convert_to_pygame(position), radius, border)

    @staticmethod
    def draw_rect(rect, color=(0, 0, 0), border=0):

        pos = rect[0]
        pos = pos[0], pos[1] + rect[1][1] - 1
        pos = Render.convert_to_pygame(pos)

        rect = pos, rect[1]

        pygame.draw.rect(pygame.display.get_surface(), color, rect, border)

    @staticmethod
    def draw_line(p1, p2, color=(0, 0, 0), border=1):

        p1 = Render.convert_to_pygame(p1)
        p2 = Render.convert_to_pygame(p2)

        pygame.draw.line(pygame.display.get_surface(),
                         color,
                         p1,
                         p2,
                         border)

    @staticmethod
    def draw_lines(points, color=(0, 0, 0)):

        converted_points = deepcopy(points)

        for i in range(len(converted_points)):
            converted_points[i] = Render.convert_to_pygame(converted_points[i])

        pygame.draw.lines(pygame.display.get_surface(),
                          color,
                          False,
                          converted_points)

    @staticmethod
    def center_on(pos):

        if pos is None:
            Render.offset = 0, 0
            return

        x = Render.width / 2 - pos[0]
        y = Render.height / 2 - pos[1]

        Render.offset = x, y

    @staticmethod
    def calc_offset(pos):

        if pos is None:
            Render.offset = 0, 0
            return

        x = Render.width / 2 - pos[0]
        y = Render.height / 2 - pos[1]

        return x, y
