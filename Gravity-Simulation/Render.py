import pygame


class Render:

    width = 0
    height = 0

    screen_top = 0
    screen_bottom = 0
    screen_left = 0
    screen_right = 0

    @staticmethod
    def set_surface(surface):

        Render.width, Render.height = surface.get_size()

        Render.screen_top = Render.height / 2
        Render.screen_bottom = -Render.height / 2
        Render.screen_left = -Render.width / 2
        Render.screen_right = Render.width / 2

    @staticmethod
    def convert_point(point):

        center_x = Render.width / 2
        center_y = Render.height / 2

        return (int(center_x + point[0]),
                int(center_y - point[1]))

    @staticmethod
    def draw_circle(position, radius=5, color=(0, 0, 0), border=0):

        pygame.draw.circle(pygame.display.get_surface(), color, Render.convert_point(position), radius, border)

    @staticmethod
    def draw_rect(rect, color=(0, 0, 0), border=0):

        pos = rect[0]
        pos = pos[0], pos[1] + rect[1][1] - 1
        pos = Render.convert_point(pos)

        rect = pos, rect[1]

        pygame.draw.rect(pygame.display.get_surface(), color, rect, border)

    @staticmethod
    def draw_line(p1, p2, color=(0, 0, 0), border=1):

        p1 = Render.convert_point(p1)
        p2 = Render.convert_point(p2)

        pygame.draw.line(pygame.display.get_surface(),
                         color,
                         p1,
                         p2,
                         border)
