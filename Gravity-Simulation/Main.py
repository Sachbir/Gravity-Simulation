import pygame
import sys
from time import time
from copy import deepcopy

import config
from Body import Body, Calc
from Render import Render
from UI import UIBar


class Simulation:

    pygame.init()

    def __init__(self):

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.window_size)

        Render.set_surface(pygame.display.get_surface())
        UIBar.set_surface(pygame.display.get_surface())

        num_obj = 1

        self.isPaused = True

        self.allBodies = []
        b = Body()
        b.mass = 100
        b.radius = 10
        b.position = config.window_size[0] / 2 - 400, config.window_size[1] / 2
        b.position = 0, 0
        b.name = "Body_" + str(len(self.allBodies))
        self.allBodies.append(b)

        self.focus_body = self.allBodies[0]
        self.selected_body = self.allBodies[0]

        self.dict = {}
        self.set_event_dict()

        self.paths_calculated = False
        self.details_bar = None

    def run(self):

        barWidth = 250
        barHeight = config.window_size[1]

        barX = config.window_size[0] - barWidth
        barY = 0

        self.details_bar = UIBar("Details", barX, barY, barWidth, barHeight)

        frame_num = 0

        while True:

            # frame_start_time = time()

            self.clock.tick(config.UPS_max)
            pygame.display.flip()
            frame_num += 1

            # frame_start_time = time()

            self.event_processing()

            self.screen.fill((0, 0, 0))

            if not self.isPaused:
                for o in self.allBodies:
                    o.update_velocity(self.allBodies)
                for o in self.allBodies:
                    o.update_position()

            self.render_bodies()    # TODO: Figure out why this has to be done *before* calculating paths
            if self.isPaused:
                self.calc_future_paths()
                self.draw_future_paths()
                self.render_bodies()

            if self.isPaused:
                self.details_bar.render()

            # Simulation.measure_update_time(frame_start_time)

    def redraw(self):

        self.screen.fill((0, 0, 0))
        self.calc_future_paths()
        self.render_bodies()
        self.details_bar.render()

    def render_bodies(self):

        if self.focus_body is not None:
            Render.center_on(self.focus_body.position)
        else:
            Render.center_on((0, 0))

        for o in self.allBodies:
            o.render()

    def event_processing(self):
        """Checks for any and all events occurring during runtime"""

        if config.frame_counter % 3 == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # End simulation
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    self.get_dict(event.key)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.isPaused:
                    # get coordinates of the click
                    mouse_pos = pygame.mouse.get_pos()
                    pos = Render.convert_to_renderer(mouse_pos)

                    flag = 0

                    # check for a collision with any body
                    for body in self.allBodies:
                        if body.collide_point(pos):
                            flag = 1
                            self.selected_body = body
                            # self.render_bodies()
                            # if we find a collision, no need to check further
                            break

                    # No collision: Make new body
                    if flag == 0:
                        o = Body(pos)
                        o.name = "Body_" + str(len(self.allBodies))
                        o.render()
                        self.allBodies.append(o)
                        self.selected_body = o
                        self.paths_calculated = False

                    # if a collision is found...
                    self.update_event_dict()    # with the new selected body
                    self.details_bar.update(self.selected_body)

    # noinspection PyPep8Naming
    @staticmethod
    def measure_update_time(time_start):
        """Takes the beginning and end time of the cycle to determine how fast the system is actually operating at"""

        tim_end = time()
        time_elapsed = tim_end - time_start

        # When the frame renders as fast as possible (minimal/zero values), UPS reaches the maximum allowed
        try:
            measured_UPS = min((1 / time_elapsed), config.UPS_max)
        except ZeroDivisionError:
            measured_UPS = 120
        config.UPS_measurement_tracker += measured_UPS

        config.frame_counter += 1
        if config.frame_counter == config.frames_to_measure:
            print("Measured UPS: " + str(config.UPS_measurement_tracker / config.frames_to_measure))
            config.UPS_measurement_tracker = 0
            config.frame_counter = 0

    def get_dict(self, key):

        try:
            self.dict[key]()
            self.update_calc_rendering()
        except KeyError:
            pass

    def set_event_dict(self):

        self.dict[pygame.K_SPACE] = self.toggle_pause
        self.dict[pygame.K_q] = sys.exit
        self.dict[pygame.K_r] = self.__init__
        self.dict[pygame.K_f] = self.change_focus_body

    def update_event_dict(self):
        self.dict[pygame.K_EQUALS] = self.selected_body.mass_inc
        self.dict[pygame.K_MINUS] = self.selected_body.mass_dec
        self.dict[pygame.K_UP] = self.selected_body.vel_y_inc
        self.dict[pygame.K_DOWN] = self.selected_body.vel_y_dec
        self.dict[pygame.K_LEFT] = self.selected_body.vel_x_dec
        self.dict[pygame.K_RIGHT] = self.selected_body.vel_x_inc

    def change_focus_body(self):

        self.focus_body = self.selected_body
        self.center_values_on_focus()
        self.paths_calculated = False

    def center_values_on_focus(self):

        if self.focus_body is None:
            return

        temp = deepcopy(self.focus_body)

        for body in self.allBodies:
            body.velocity = Calc.sub_vector2(body.velocity, temp.velocity)
            body.position = Calc.sub_vector2(body.position, temp.position)

    def update_calc_rendering(self):

        self.paths_calculated = False
        self.details_bar.update(self.selected_body)

    def toggle_pause(self):

        self.isPaused = not self.isPaused
        self.center_values_on_focus()
        self.paths_calculated = False
        self.details_bar.update(self.selected_body)

    def calc_future_paths(self):

        if not self.paths_calculated:

            num_predictions = 1000

            for body in self.allBodies:
                body.future_velocities = []
                body.future_positions = []

            for i in range(num_predictions):
                for body in self.allBodies:
                    body.calc_future_velocity(self.allBodies, i)
                    body.calc_future_position(i)

            if self.focus_body is not None:
                for body in self.allBodies:
                    if body is self.focus_body:
                        continue
                    for i in range(len(body.future_positions)):
                        future_offset = Calc.sub_vector2(Render.offset,
                                                         Render.calc_offset(self.focus_body.future_positions[i]))

                        body.future_positions[i] = Calc.sub_vector2(body.future_positions[i],
                                                                    future_offset)

        self.paths_calculated = True

    def draw_future_paths(self):

        for body in self.allBodies:
            if body is not self.focus_body:
                body.render_paths()


sim = Simulation()
sim.run()

# References
# https://stackoverflow.com/questions/23841128/pygame-how-to-check-mouse-coordinates
# https://stackoverflow.com/questions/12150957/pygame-action-when-mouse-click-on-rect
