import pygame
import sys
from copy import deepcopy
from time import time

import config
from Body import Body, Calc
from Render import Render
from UI import UIPanel


class Simulation:

    pygame.init()

    def __init__(self):

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.window_size)

        Render.set_surface(pygame.display.get_surface())

        self.allBodies = [
            Body(name="Star_1", position=(0, 0), mass=500, colour=(255, 255, 186)),
            Body(name="Star_2", position=(-40, 0), mass=500, velocity=(0, -4.84), colour=(255, 255, 186)),
            Body(name="Earth", position=(-250, 0), mass=10, velocity=(0, -4.5), colour=(186, 255, 255)),
            Body(name="Moon", position=(-265, 0), mass=1, velocity=(0, -5.39), colour=(255, 255, 255))
        ]

        self.KeyPressDict = {}
        self.init_key_press_dict()

        self.focus_point = None
        self.focus_bodies = [self.allBodies[0], self.allBodies[1]]
        self.set_focus_point()

        self.paths_calculated = False
        self.isPaused = True

        self.details_bar = None
        self.create_details_sidebar()

        self.is_in_input_mode = False

        self.selected_bodies = []
        self.selected_input_obj = None

    def do_when_selected_bodies_changed(self):

        self.update_event_dict_for_new_selection()
        if self.details_bar is not None:
            if len(self.selected_bodies) > 0:
                self.details_bar.selected_objects = self.selected_bodies
            else:
                self.details_bar.selected_objects = []

    @property
    def selected_input_obj(self):
        return self.__selected_input_obj

    @selected_input_obj.setter
    def selected_input_obj(self, selected_input_obj):

        if selected_input_obj is None:
            self.details_bar.is_field_selected = False
        else:
            self.details_bar.is_field_selected = True

        self.__selected_input_obj = selected_input_obj

    def run(self):

        while True:

            # frame_start_time = time()

            self.clock.tick(config.UPS)
            pygame.display.flip()

            self.event_processing()

            if not self.isPaused:
                for o in self.allBodies:
                    o.update_velocity(self.allBodies)
                for o in self.allBodies:
                    o.update_position()
                self.set_focus_point(False)
            else:
                self.set_focus_point()

            self.screen.fill((0, 0, 0))
            self.center_frame_on_focus()
            if self.isPaused:
                self.calc_future_paths()
                self.draw_future_paths()

            for o in self.allBodies:
                o.render()

            if self.isPaused:
                if len(self.selected_bodies) > 0:
                    for body in self.selected_bodies:
                        body.render_select_bubble()
                self.details_bar.render()

            # Simulation.measure_update_time(frame_start_time)

    def set_focus_point(self, copy_path=True):

        if len(self.focus_bodies) == 0:
            self.focus_point = None
            return

        if self.focus_point is None:
            self.focus_point = Body((-100, -100), name="Focus_Point")   # loc doesn't matter, never used or rendered

        self.focus_point.position = deepcopy(self.focus_bodies[0].position)
        if copy_path:
            self.focus_point.future_positions = deepcopy(self.focus_bodies[0].future_positions)

        if len(self.focus_bodies) > 1:
            for i in range(1, len(self.focus_bodies)):
                body = self.focus_bodies[i]
                self.focus_point.position = Calc.add_vector2(self.focus_point.position,
                                                             body.position)

            self.focus_point.position = Calc.multiply_vector2_by_factor(self.focus_point.position,
                                                                        (1 / len(self.focus_bodies)))

            if not copy_path:
                return

            for i in range(1, len(self.focus_bodies)):
                body = self.focus_bodies[i]
                for j in range(len(self.focus_point.future_positions)):
                    self.focus_point.future_positions[j] = Calc.add_vector2(self.focus_point.future_positions[j],
                                                                            body.future_positions[j])
            for i in range(len(self.focus_point.future_positions)):
                self.focus_point.future_positions[i] = \
                    Calc.multiply_vector2_by_factor(self.focus_point.future_positions[i],
                                                    (1 / len(self.focus_bodies)))

    def center_frame_on_focus(self):

        if self.focus_point is not None:
            Render.center_on(self.focus_point.position)
        else:
            Render.center_on((0, 0))

    def event_processing(self):
        """Checks for any and all events occurring during runtime"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # End simulation
                sys.exit(0)

            elif event.type == pygame.KEYDOWN:
                if self.selected_input_obj is not None:
                    input_box = self.selected_input_obj
                    input_box.handle_user_input(event)
                    if not input_box.is_selected:
                        self.selected_input_obj = None
                        self.paths_calculated = False
                    self.details_bar.update()
                else:
                    self.handle_keypress_event(event.key)

            # Handle mouse click
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.isPaused:

                # Check if the UI was clicked
                mouse_pos = pygame.mouse.get_pos()
                was_ui_clicked = self.handle_ui_click(mouse_pos)
                if was_ui_clicked:
                    continue

                self.handle_sim_space_click(mouse_pos)

    def handle_sim_space_click(self, mouse_pos):

        # Check if a body was clicked
        pos = Render.convert_to_renderer(mouse_pos)
        body_clicked = None
        # check for a collision with any body
        for body in self.allBodies:
            if body.click_point(pos):
                body_clicked = body
                break

        if body_clicked is not None:
            # If a body is clicked, select/deselect it
            if body_clicked in self.selected_bodies:
                self.selected_bodies.remove(body_clicked)
            else:
                self.selected_bodies.append(body_clicked)
            if len(self.selected_bodies) > 0:
                self.details_bar.selected_objects = self.selected_bodies
            else:
                self.details_bar.selected_objects = []
        else:
            # If no body is clicked, either deselect all, or create new body
            if len(self.selected_bodies) != 0:
                self.selected_bodies = []
            else:
                o = Body(pos)
                self.allBodies.append(o)
                self.selected_bodies.append(o)
                self.paths_calculated = False

        self.do_when_selected_bodies_changed()
        self.details_bar.update(True)

    def handle_ui_click(self, mouse_pos):

        obj_clicked = self.details_bar.get_input_box_clicked(mouse_pos)

        # If an input box was previously selected, deselected it
        if self.selected_input_obj is not None:
            self.selected_input_obj.is_selected = False

        if obj_clicked is not None:
            if obj_clicked == self.selected_input_obj:
                # If the object clicked was already selected, deselect it
                self.selected_input_obj = None
            else:
                # Otherwise replace it with the new object
                self.selected_input_obj = obj_clicked
                self.selected_input_obj.is_selected = True
            self.details_bar.update()
            return True
        elif obj_clicked is None and self.selected_input_obj is not None:
            self.selected_input_obj = obj_clicked
            self.details_bar.update()
            return True

        # No interaction occurred
        return False

    # noinspection PyPep8Naming
    @staticmethod
    def measure_update_time(time_start):
        """Takes the beginning and end time of the cycle to determine how fast the system is actually operating at"""

        time_end = time()
        time_elapsed = time_end - time_start

        # When the frame renders as fast as possible (minimal/zero values), UPS reaches the maximum allowed
        try:
            measured_UPS = min((1 / time_elapsed), config.UPS)
        except ZeroDivisionError:
            measured_UPS = 120
        config.UPS_measurement_tracker += measured_UPS

        config.frame_counter += 1
        if config.frame_counter == config.frames_to_measure:
            print("Measured UPS: " + str(config.UPS_measurement_tracker / config.frames_to_measure))
            config.UPS_measurement_tracker = 0
            config.frame_counter = 0

    def handle_keypress_event(self, key):

        try:
            self.KeyPressDict[key]()
            self.paths_calculated = False
            self.details_bar.update()
        except KeyError:
            # Ignore keys that don't exist in the dictionary
            pass

    def init_key_press_dict(self):

        self.KeyPressDict[pygame.K_SPACE] = self.toggle_pause
        self.KeyPressDict[pygame.K_q] = sys.exit
        self.KeyPressDict[pygame.K_r] = self.__init__
        self.KeyPressDict[pygame.K_f] = self.change_focus_body

    def update_event_dict_for_new_selection(self):

        self.KeyPressDict = {}
        self.init_key_press_dict()

        if len(self.selected_bodies) == 0:
            return

        if len(self.selected_bodies) > 0:
            self.KeyPressDict[pygame.K_DELETE] = self.delete_selected
            self.KeyPressDict[pygame.K_BACKSPACE] = self.delete_selected
        if len(self.selected_bodies) == 1:
            self.KeyPressDict[pygame.K_EQUALS] = self.selected_bodies[0].mass_inc
            self.KeyPressDict[pygame.K_MINUS] = self.selected_bodies[0].mass_dec
            self.KeyPressDict[pygame.K_UP] = self.selected_bodies[0].vel_y_inc
            self.KeyPressDict[pygame.K_DOWN] = self.selected_bodies[0].vel_y_dec
            self.KeyPressDict[pygame.K_LEFT] = self.selected_bodies[0].vel_x_dec
            self.KeyPressDict[pygame.K_RIGHT] = self.selected_bodies[0].vel_x_inc
        # No special functions for multiple objects (for now)

    def delete_selected(self):

        for body in self.selected_bodies:
            self.allBodies.remove(body)
            if body in self.focus_bodies:
                self.focus_bodies.remove(body)
        self.selected_bodies = []

        if len(self.focus_bodies) == 0:
            if len(self.allBodies) > 0:
                self.focus_bodies = [self.allBodies[0]]
            else:
                self.focus_bodies = []
        self.set_focus_point()

    def change_focus_body(self):

        self.focus_bodies = [body for body in self.selected_bodies]
        self.set_focus_point()
        self.center_values_on_focus()
        self.paths_calculated = False

    def center_values_on_focus(self):

        if self.focus_point is None:
            return

        for body in self.allBodies:
            body.center_values_on_focus_body(self.focus_point)

    def toggle_pause(self):

        self.isPaused = not self.isPaused
        self.center_values_on_focus()
        self.paths_calculated = False
        self.details_bar.update()

    def calc_future_paths(self):

        if self.paths_calculated:
            return

        for body in self.allBodies:
            body.predictions_reset()

        for i in range(config.num_future_predictions):
            for body in self.allBodies:
                body.prediction_velocities(self.allBodies, i)
            for body in self.allBodies:
                body.prediction_positions(i)

        if len(self.focus_bodies) > 0:
            self.set_focus_point()

            for body in self.allBodies:
                body.predictions_center_on_focus_body(self.focus_point)
                if body.path_colour == Body.path_colour_collision:
                    self.isPaused = True

        self.paths_calculated = True

    def draw_future_paths(self):

        for body in self.allBodies:
            body.render_paths()

    def create_details_sidebar(self):

        bar_width = 250
        bar_height = config.window_size[1]

        bar_x = config.window_size[0] - bar_width
        bar_y = 0

        self.details_bar = UIPanel(pygame.display.get_surface(), "Details", bar_x, bar_y, bar_width, bar_height)


sim = Simulation()
sim.run()
