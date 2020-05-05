import pygame
import pygame.freetype
from Body import Body
from Mutability import Mutability


pygame.font.init()
pygame.freetype.init()
system_font = pygame.freetype.get_default_font()


class UIBar:

    padding = 30
    leading = 10

    font_title = pygame.freetype.SysFont(system_font, 30)
    font_default = pygame.freetype.SysFont(system_font, 15)

    surface = None

    def __init__(self, title, x, y, width, height):

        self.title = title

        self.location = x, y
        self.dimensions = width, height

        self.start_draw_location = UIBar.padding, UIBar.padding
        self.draw_location = 0, 0

        self.s = None
        self.fields = []
        self.selected_field = None
        self.selected_object = None

        self.update()

        self.input_string = ""

    def render(self):

        UIBar.surface.blit(self.s, self.location)

    def update(self):

        self.s = pygame.Surface(self.dimensions)
        self.s.set_alpha(128)
        self.s.fill((255, 255, 255))

        self.draw_location = self.start_draw_location

        self.draw_text(UIBar.font_title, self.title)

        if self.selected_object is not None:
            for prop in Body.ui_properties:
                self.add_property(prop)

        if self.selected_field is not None:
            self.highlight_selected_field()

    def draw_text(self, font, text):

        font.render_to(self.s, self.draw_location, text)
        self.draw_location = (self.draw_location[0],
                              self.draw_location[1] + font.size + UIBar.leading)

    def draw_property(self, prop_name):

        if self.selected_field is not None and \
                self.selected_field.prop_name == prop_name and \
                self.input_string != "":
            val = self.input_string + "|"
        else:
            val = UIBar.stringify_property(getattr(self.selected_object, prop_name))

        text = prop_name + ":  " + val
        self.draw_text(UIBar.font_default, text)

    def add_property(self, prop_info):

        start_pos = (UIBar.padding,
                     self.draw_location[1])
        self.draw_property(prop_info[0])
        end_pos = (self.dimensions[0] - 2 * UIBar.padding,
                   self.draw_location[1])

        prop = UIField(prop_info, start_pos, end_pos)
        self.fields.append(prop)

    def collide_point(self, point):

        if (self.location[0] < point[0] < (self.location[0] + self.dimensions[0]) and
                self.location[1] < point[1] < (self.location[1] + self.dimensions[1])):
            return True
        return False

    def handle_click(self, mouse_pos):

        pos = mouse_pos[0] - self.location[0], mouse_pos[1] - self.location[1]

        for field in self.fields:
            field_clicked = field.does_point_collide(pos)
            if field_clicked:
                if self.selected_field == field or \
                        field.mutability == Mutability.NONE:
                    self.selected_field = None
                    return False
                self.selected_field = field
                return True

        return False

    def highlight_selected_field(self):

        p0 = self.selected_field.p0[0] - 1, self.selected_field.p0[1] - 1
        width = self.dimensions[0] - 2 * UIBar.padding
        height = self.font_default.size + 1

        pygame.draw.rect(self.s, (255, 55, 55), (p0, (width, height)), 1)

    def deselect_fields(self):

        self.selected_field = None
        self.input_string = ""

    def handle_user_input(self, event):

        if self.selected_field.mutability == Mutability.NUM:
            return self.handle_user_input_num(event)
        elif self.selected_field.mutability == Mutability.STR:
            return self.handle_user_input_str(event)

    def handle_user_input_num(self, event):
        """ Used to add/remove numbers to the input
            Returns whether the input is complete or not """

        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.input_string = self.input_string[:-1]
        elif event.unicode.isdigit() or event.unicode == "." or event.unicode == "-":
            self.input_string += event.unicode
        elif keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
            if self.input_string != "":
                setattr(self.selected_object, self.selected_field.prop_name, float(self.input_string))
            self.deselect_fields()
            return False  # Input is complete
        return True  # Input still in progress

    def handle_user_input_str(self, event):
        """ Used to add/remove characters to the input
            Returns whether the input is complete or not """

        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.input_string = self.input_string[:-1]
        elif event.unicode.isalnum() or event.unicode == "_":
            self.input_string += event.unicode
        elif keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
            if self.input_string != "":
                setattr(self.selected_object, self.selected_field.prop_name, self.input_string)
            self.deselect_fields()
            return False  # Input is complete
        return True  # Input still in progress

    @staticmethod
    def stringify_property(val):

        if isinstance(val, (int, float)):
            return str(round(val, 2))
        else:
            return str(val)

    @staticmethod
    def set_surface(surface):

        UIBar.surface = surface


class UIField:

    def __init__(self, prop_info, p0, p1):

        self.prop_name = prop_info[0]
        self.mutability = prop_info[1]
        self.p0 = p0
        self.p1 = p1

    def does_point_collide(self, point):

        if (self.p0[0] <= point[0] <= self.p1[0] and
                self.p0[1] <= point[1] <= self.p1[1]):
            return True
        return False


# TODO: record location of each property, so when a user clicks there, they can edit the values
