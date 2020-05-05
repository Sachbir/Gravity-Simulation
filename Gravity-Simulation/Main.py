import pygame
import sys
from time import time

import config
from Body import Body
from Render import Render
from UI import UIBar


class Simulation:

    pygame.init()

    def __init__(self):

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.window_size)

        Render.set_surface(pygame.display.get_surface())
        UIBar.set_surface(pygame.display.get_surface())

        self.allBodies = []
        name = "Body_" + str(len(self.allBodies))
        b = Body(name, (0, 0))
        b.mass = 100
        self.allBodies.append(b)

        self.EventDict = {}
        self.set_event_dict()

        self.focus_body = self.allBodies[0]

        self.paths_calculated = False
        self.isPaused = True

        self.details_bar = None
        self.create_details_sidebar()

        self.is_in_input_mode = False

        self.selected_body = None

    @property
    def selected_body(self):
        return self.__selected_body

    @selected_body.setter
    def selected_body(self, selected_body):

        self.__selected_body = selected_body
        self.update_event_dict_for_new_selection()
        if self.details_bar is not None:
            self.details_bar.selected_object = selected_body

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

            self.screen.fill((0, 0, 0))
            self.center_frame_on_focus()
            if self.isPaused:
                self.calc_future_paths()
                self.draw_future_paths()

            for o in self.allBodies:
                o.render()

            if self.isPaused:
                if self.selected_body is not None:
                    self.selected_body.render_select_bubble()
                self.details_bar.render()

            # Simulation.measure_update_time(frame_start_time)

    def center_frame_on_focus(self):

        if self.focus_body is not None:
            Render.center_on(self.focus_body.position)
        else:
            Render.center_on((0, 0))

    def event_processing(self):
        """Checks for any and all events occurring during runtime"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # End simulation
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if self.is_in_input_mode:
                    self.is_in_input_mode = self.details_bar.handle_user_input(event)
                    self.details_bar.update()
                    if not self.is_in_input_mode:
                        self.paths_calculated = False
                else:
                    self.handle_keypress_event(event.key)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.isPaused:
                # get coordinates of the click
                mouse_pos = pygame.mouse.get_pos()
                pos = Render.convert_to_renderer(mouse_pos)



                was_ui_field_clicked = self.details_bar.handle_click(mouse_pos)

                # is_field_selected = self.details_bar.selected_field is not None

                # First try UI click
                if was_ui_field_clicked:
                    self.is_in_input_mode = True
                    self.details_bar.update()
                    continue

                # If user clicked outside UI while in input mode, cancel click and continue
                if self.is_in_input_mode:
                    # If anything else was clicked, deselect the details bar (if still highlighted)
                    self.details_bar.deselect_fields()
                    self.details_bar.update()
                    self.is_in_input_mode = False
                    continue

                # Then check if a body was clicked
                was_body_clicked = False

                # check for a collision with any body
                for body in self.allBodies:
                    if body.click_point(pos):
                        was_body_clicked = True
                        self.selected_body = body
                        # self.render_bodies()
                        # if we find a collision, no need to check further
                        break

                # Finally if nothing was clicked, you can make a new body
                if not was_body_clicked:
                    name = "Body_" + str(len(self.allBodies))
                    o = Body(name, pos)
                    self.allBodies.append(o)
                    self.selected_body = o
                    self.paths_calculated = False

                self.details_bar.update()

    # noinspection PyPep8Naming
    @staticmethod
    def measure_update_time(time_start):
        """Takes the beginning and end time of the cycle to determine how fast the system is actually operating at"""

        tim_end = time()
        time_elapsed = tim_end - time_start

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
            self.EventDict[key]()
            self.paths_calculated = False
            self.details_bar.update()
        except KeyError:
            # Ignore keys that don't exist in the dictionary
            pass

    def set_event_dict(self):

        self.EventDict[pygame.K_SPACE] = self.toggle_pause
        self.EventDict[pygame.K_q] = sys.exit
        self.EventDict[pygame.K_r] = self.__init__
        self.EventDict[pygame.K_f] = self.change_focus_body

    def update_event_dict_for_new_selection(self):

        if self.selected_body is None:
            try:
                del self.EventDict[pygame.K_EQUALS]
                del self.EventDict[pygame.K_MINUS]
                del self.EventDict[pygame.K_UP]
                del self.EventDict[pygame.K_DOWN]
                del self.EventDict[pygame.K_LEFT]
                del self.EventDict[pygame.K_RIGHT]
            except KeyError:
                pass    # If the key doesn't exist, it's fine. That's the whole point
        else:
            self.EventDict[pygame.K_EQUALS] = self.selected_body.mass_inc
            self.EventDict[pygame.K_MINUS] = self.selected_body.mass_dec
            self.EventDict[pygame.K_UP] = self.selected_body.vel_y_inc
            self.EventDict[pygame.K_DOWN] = self.selected_body.vel_y_dec
            self.EventDict[pygame.K_LEFT] = self.selected_body.vel_x_dec
            self.EventDict[pygame.K_RIGHT] = self.selected_body.vel_x_inc

    def change_focus_body(self):

        self.focus_body = self.selected_body
        self.center_values_on_focus()
        self.paths_calculated = False

    def center_values_on_focus(self):

        if self.focus_body is None:
            return

        for body in self.allBodies:
            if body == self.focus_body:
                continue    # Do this last do it doesn't interfere with calculations of other bodies
            body.center_values_on_focus_body(self.focus_body)
        self.focus_body.center_values_on_focus_body(self.focus_body)

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

        if self.focus_body is not None:
            for body in self.allBodies:
                if body is self.focus_body:
                    continue
                body.predictions_center_on_focus_body(self.focus_body)

        self.paths_calculated = True

    def draw_future_paths(self):

        for body in self.allBodies:
            if body is not self.focus_body:
                body.render_paths()

    def create_details_sidebar(self):

        bar_width = 250
        bar_height = config.window_size[1]

        bar_x = config.window_size[0] - bar_width
        bar_y = 0

        self.details_bar = UIBar("Details", bar_x, bar_y, bar_width, bar_height)


sim = Simulation()
sim.run()
