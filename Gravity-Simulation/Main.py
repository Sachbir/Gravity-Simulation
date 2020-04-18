import pygame
import sys
from time import time

import config
from Object import Object
from Body import Body
from Render import Render


class Simulation:

    pygame.init()

    def __init__(self):

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(config.window_size)

        Render.set_surface(pygame.display.get_surface())

        num_obj = 1

        self.isPaused = False

        self.objects = []
        for i in range(num_obj):
            # self.objects.append(Object())
            self.objects.append(Body())

        self.dict = {}
        self.set_event_dict()

    def run(self):

        frame_num = 0

        while True:

            # frame_start_time = time()

            self.clock.tick(config.UPS_max)
            pygame.display.flip()
            frame_num += 1

            # frame_start_time = time()

            self.event_processing()

            if self.isPaused:
                continue

            self.screen.fill((0, 0, 0))

            # for o in self.objects:
            #     o.check_for_collisions(self.objects)
            # for o in self.objects:
            #     o.calculate(self.objects)
            # for o in self.objects:
            #     o.update_and_render()

            for o in self.objects:
                o.update_velocity()
            for o in self.objects:
                o.update_position()
            for o in self.objects:
                o.render()

            # Simulation.measure_update_time(frame_start_time)

    def event_processing(self):
        """Checks for any and all events occurring during runtime"""

        if config.frame_counter % 3 == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # End simulation
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    self.get_dict(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.isPaused:
                    mouse_pos = pygame.mouse.get_pos()
                    pos = Render.convert_to_renderer(mouse_pos)
                    o = Body(pos)
                    o.render()
                    self.objects.append(o)

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


sim = Simulation()
sim.run()

# References
# https://stackoverflow.com/questions/23841128/pygame-how-to-check-mouse-coordinates
# https://stackoverflow.com/questions/12150957/pygame-action-when-mouse-click-on-rect
