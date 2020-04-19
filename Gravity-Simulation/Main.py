import pygame
import sys
from time import time

import config
from Body import Body, Calc
from Render import Render


class Simulation:

    pygame.init()

    def __init__(self):

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.window_size)

        Render.set_surface(pygame.display.get_surface())

        num_obj = 1

        self.isPaused = False

        self.allBodies = []
        # for i in range(num_obj):
        b = Body()
        b.mass = 200
        b.radius = 10
        b.position = config.window_size[0] / 2 - 400, config.window_size[1] / 2
        b.position = 0, 0
        self.allBodies.append(b)

        b = Body()
        b.mass = 10
        b.radius = 5
        b.position = config.window_size[0] / 2 - 400, config.window_size[1] / 2
        b.position = 100, 100
        b.velocity = 10, 0
        self.allBodies.append(b)

        self.dict = {}
        self.set_event_dict()

        self.object_selected = None

    def run(self):

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
            # else:
            self.draw_future_paths()

            self.render_bodies()

            # Simulation.measure_update_time(frame_start_time)

    def render_bodies(self):

        if self.object_selected is not None:
            Render.center_on(self.object_selected.position)
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
                    mouse_pos = pygame.mouse.get_pos()
                    pos = Render.convert_to_renderer(mouse_pos)

                    flag = 0

                    for body in self.allBodies:
                        if body.collide_point(pos):
                            flag = 1
                            self.object_selected = body
                            self.render_bodies()
                            break

                    # No collision: Make new body
                    if flag == 0:
                        o = Body(pos)
                        o.render()
                        self.allBodies.append(o)

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
        except KeyError:
            pass

    def set_event_dict(self):

        self.dict[pygame.K_SPACE] = self.toggle_pause
        self.dict[pygame.K_q] = sys.exit
        self.dict[pygame.K_r] = self.__init__

    def toggle_pause(self):

        self.isPaused = not self.isPaused

    def draw_future_paths(self):

        num_predictions = 100

        for body in self.allBodies:
            body.future_velocities = []
            body.future_positions = []

        for i in range(num_predictions):
            for body in self.allBodies:
                body.calc_future_velocity(self.allBodies, i)
                body.calc_future_position(i)

        if self.object_selected is not None:
            for body in self.allBodies:
                if body is self.object_selected:
                    continue
                for i in range(len(body.future_positions)):
                    future_offset = Calc.sub_vector2(Render.offset,
                                                     Render.calc_offset(self.object_selected.future_positions[i]))

                    body.future_positions[i] = Calc.sub_vector2(body.future_positions[i],
                                                                future_offset)

        for body in self.allBodies:
            if body is not self.object_selected:
                body.render_paths()


sim = Simulation()
sim.run()

# References
# https://stackoverflow.com/questions/23841128/pygame-how-to-check-mouse-coordinates
# https://stackoverflow.com/questions/12150957/pygame-action-when-mouse-click-on-rect
