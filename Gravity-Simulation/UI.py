import pygame
import pygame.freetype


pygame.font.init()
pygame.freetype.init()
system_font = pygame.freetype.get_default_font()


class UIBar:

    text_title_height = 30
    text_height = 15

    margin_height = 10

    text_title = pygame.freetype.SysFont(system_font, text_title_height)
    text = pygame.freetype.SysFont(system_font, text_height)

    surface = None

    def __init__(self, title, x, y, width, height):

        self.title = title

        self.location = x, y
        self.dimensions = width, height

        self.start_draw_location = 30, 30
        self.draw_location = 0, 0

        self.s = None
        self.update()

    def render(self):

        UIBar.surface.blit(self.s, self.location)  # (0,0) are the top-left coordinates

    def update(self, selected_object=None):

        self.s = pygame.Surface(self.dimensions)  # the size of your rect
        self.s.set_alpha(128)  # alpha level
        self.s.fill((255, 255, 255))  # this fills the entire surface

        self.draw_location = self.start_draw_location

        self.draw_title()

        if selected_object is not None:
            self.draw_property(selected_object.name)
            display_velocity = (round(selected_object.velocity[0], 2),
                                round(selected_object.velocity[1], 2))
            self.draw_property("Velocity:")
            self.draw_property("    X: " + str(round(display_velocity[0], 2)))
            self.draw_property("    Y: " + str(round(display_velocity[1], 2)))
            self.draw_property("Mass: " + str(round(selected_object.mass, 2)))
            self.draw_property("Radius: " + str(round(selected_object.radius, 2)))

    def draw_title(self):

        UIBar.text_title.render_to(self.s, self.draw_location,
                                   self.title)
        self.draw_location = (self.draw_location[0],
                              self.draw_location[1] + UIBar.text_title_height + UIBar.margin_height)

    def draw_property(self, text):

        UIBar.text.render_to(self.s, self.draw_location,
                             text)
        self.draw_location = (self.draw_location[0],
                              self.draw_location[1] + UIBar.text_height + UIBar.margin_height)

    def collide_point(self, point):

        if (self.location[0] < point[0] < (self.location[0] + self.dimensions[0]) and
                self.location[1] < point[1] < (self.location[1] + self.dimensions[1])):
            return True
        return False

    def handle_click(self, point):

        pass

    @staticmethod
    def set_surface(surface):

        UIBar.surface = surface


