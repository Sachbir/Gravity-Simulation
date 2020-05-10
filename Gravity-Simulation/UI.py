import pygame
import pygame.freetype
from Body import Body
from Mutability import Mutability


pygame.font.init()
pygame.freetype.init()
system_font = pygame.freetype.get_default_font()

font_title = pygame.freetype.SysFont(system_font, 30)
font_default = pygame.freetype.SysFont(system_font, 15)
leading = 10

no_select_text = ["No object selected.",
                  "Click an object to select",
                  " it, or click an empty space",
                  " to create a new one."]
single_select_text = ["Press F to keep the camera",
                      " focused on this object.",
                      "Press Del/Backspace to",
                      " delete it."]
multi_select_text = ["Multiple objects selected.",
                     "Press F to keep the camera",
                     " focus on these objects.",
                     "Press Del/Backspace to",
                     " delete them."]


class UIPanel:

    padding = 30

    def __init__(self, main_window, title, x, y, width, height):

        self.MainWindow = main_window

        self.title = title
        self.location = x, y
        self.dimensions = width, height

        self.start_draw_location = UIPanel.padding, UIPanel.padding
        self.start_draw_location_bottom = UIPanel.padding, self.dimensions[1] - UIPanel.padding
        self.draw_location = 0, 0
        self.draw_location_bottom = 0, 0

        self.surface = pygame.Surface(self.dimensions)
        self.surface.set_alpha(172)

        self.fields = []
        self.is_field_selected = False
        self.selected_objects = []

        self.input_string = ""

        self.update()

    def render(self):

        self.MainWindow.blit(self.surface, self.location)

    def update(self, reload_data=False):

        self.surface.fill((150, 150, 150))

        self.draw_location = self.start_draw_location
        self.draw_text(font_title, self.title)
        self.draw_text_keyboard_shortcuts()

        if len(self.selected_objects) == 0:
            self.draw_multiple_lines(no_select_text)
            return
        elif len(self.selected_objects) > 1:
            self.draw_multiple_lines(multi_select_text)
            return

        # If there *is* a selected object, do the rest of the function:

        self.draw_multiple_lines(single_select_text)

        if reload_data:
            self.fields = []
        if len(self.fields) == 0:
            for prop in Body.ui_properties:
                self.add_field(prop)
        for field in self.fields:
            field.draw()

    def draw_text(self, font, text):

        font.render_to(self.surface, self.draw_location, text)
        self.draw_location = (self.draw_location[0],
                              self.draw_location[1] + font.size + leading)

    def draw_text_from_bottom(self, font, text):

        font.render_to(self.surface, self.draw_location_bottom, text)

        self.draw_location_bottom = (self.draw_location_bottom[0],
                                     self.draw_location_bottom[1] - font.size - leading)

    def add_field(self, prop_info):

        new_field = UIField(self.surface, self.selected_objects[0], prop_info, self.draw_location)
        self.draw_location = (self.draw_location[0],
                              self.draw_location[1] + font_default.size + leading)
        self.fields.append(new_field)

    def get_input_box_clicked(self, mouse_pos):

        if len(self.fields) == 0:
            return None

        pos = mouse_pos[0] - self.location[0], mouse_pos[1] - self.location[1]

        for field in self.fields:
            if field.input_box is None:
                continue
            if field.input_box.does_point_collide(pos):
                return field.input_box

        return None

    def draw_multiple_lines(self, lines):

        for line in lines:
            self.draw_text(font_default, line)

    # Honestly, because this is a personal project I'm just going to let myself hard-code for this next function

    def draw_text_keyboard_shortcuts(self):

        self.draw_location_bottom = self.start_draw_location_bottom

        lines = ["Click the fields above to",
                 " manually enter values",
                 "Quit: Q",
                 "Pause: Space",
                 "Delete Body: Del/Backspace",
                 "Mass: +/-",
                 "Vel_X: Right/Left",
                 "Vel_Y: Up/Down"]

        if self.is_field_selected:
            lines.append("Deselect field: Click")
        elif len(self.selected_objects) > 0:
            lines.append("Select/Deselect Body: Click")
        else:
            lines.append("Select/Create Body: Click")

        for line in reversed(lines):
            self.draw_text_from_bottom(font_default, line)


class UIField:

    # Fields are grouped (/parents of) input boxes because

    # Kinda arbitrary - enough space for the field labels
    left_margin_input_box = 85

    def __init__(self, surface, obj, prop_info, p0):

        self.surface = surface
        self.obj = obj
        self.prop_name = prop_info[0]
        self.mutability = prop_info[1]
        self.p0 = p0

        self.pos_input_box = p0[0] + UIField.left_margin_input_box, p0[1]
        self.input_box = None
        if self.mutability != Mutability.NONE:
            self.input_box = InputBox(surface, self.pos_input_box, obj, prop_info[0], prop_info[1])

    @property
    def is_selected(self):
        if self.input_box is not None:
            return self.input_box.is_selected
        else:
            return False

    @is_selected.setter
    def is_selected(self, is_selected):
        self.input_box.is_selected = is_selected

    def draw(self):

        text = self.prop_name + ":  "
        font_default.render_to(self.surface, self.p0, text)

        if self.mutability != Mutability.NONE:
            self.input_box.draw()
        else:
            attr = getattr(self.obj, self.prop_name)
            if isinstance(attr, (int, float)):
                attr = str(round(attr, 2))

            font_default.render_to(self.surface, self.pos_input_box, attr)


class InputBox:

    max_char = 9

    def __init__(self, surface, p0, obj, property_name, input_type):

        self.surface = surface

        self.p0 = (p0[0] - 2, p0[1] - 2)
        self.p1 = (surface.get_width() - UIPanel.padding, p0[1] + font_default.size + 2)
        self.obj = obj
        self.property_name = property_name
        self.input_type = input_type

        self.dimensions = (self.p1[0] - p0[0],
                           self.p1[1] - p0[1])

        self.input_string = ""

        self.is_selected = False

    @property
    def is_selected(self):
        return self.__is_selected

    @is_selected.setter
    def is_selected(self, is_selected):

        self.__is_selected = is_selected
        if not is_selected:
            self.input_string = ""

    def draw(self):

        pygame.draw.rect(self.surface, (255, 255, 255), (self.p0, self.dimensions))

        position = self.p0[0] + 2, self.p0[1] + 2
        if self.input_string != "":
            font_default.render_to(self.surface, position, self.input_string)
        else:
            attr = getattr(self.obj, self.property_name)
            if isinstance(attr, (int, float)):
                attr = round(attr, 2)
            font_default.render_to(self.surface, position, str(attr))

        if self.is_selected:
            # Highlight
            pygame.draw.rect(self.surface, (255, 55, 55), (self.p0, self.dimensions), 1)

    def does_point_collide(self, point):

        return (self.p0[0] <= point[0] <= self.p1[0] and
                self.p0[1] <= point[1] <= self.p1[1])

    def handle_user_input(self, event):

        if self.input_type == Mutability.NONE:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.input_string = self.input_string[:-1]
            return

        if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
            self.save_input_value()
            return

        if len(self.input_string) >= InputBox.max_char:
            return

        if self.input_type == Mutability.NUM:
            self.validate_input_num(event)
        else:
            self.validate_input_str(event)

    def save_input_value(self):

        if self.input_string != "":
            try:
                if self.input_type == Mutability.NUM:
                    value = float(self.input_string)
                else:
                    value = self.input_string
                setattr(self.obj, self.property_name, value)
            except ValueError:
                pass    # If saving the value fails, it'll revert to the previous value by default
        self.is_selected = False

    def validate_input_num(self, event):

        if (event.unicode.isdigit() or
                (event.unicode == "-" and len(self.input_string) == 0) or   # only first character maybe a dash
                (event.unicode == "." and "." not in self.input_string)):   # '.' may only be entered once
            self.input_string += event.unicode

    def validate_input_str(self, event):

        if event.unicode.isalnum() or event.unicode == "_":
            self.input_string += event.unicode
