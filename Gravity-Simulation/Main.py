import pygame
import sys
from time import time

import config
from Object import Object


class Simulation:

    def __init__(self):

        self.objects = []
        for i in range(2):
            self.objects.append(Object())

        self.dict = {}
        self.set_event_dict()

    def run(self):

        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(config.window_size)

        frame_num = 0

        while True:

            # frame_start_time = time()

            self.event_processing()

            screen.fill((0, 0, 0))

            for o in self.objects:
                o.check_for_collisions(self.objects)
            for o in self.objects:
                o.calculate(self.objects)
            for o in self.objects:
                o.update_and_render()

            pygame.display.flip()
            frame_num += 1

            clock.tick(config.UPS_max)
            # Simulation.measure_update_time(frame_start_time)

    def event_processing(self):
        """Checks for any and all events occurring during runtime"""

        if config.frame_counter % 3 == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # End simulation
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    self.get_dict(event.key)

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

        self.dict[key]()

    def set_event_dict(self):

        self.dict[pygame.K_SPACE] = self.__init__
        self.dict[pygame.K_q] = sys.exit


sim = Simulation()
sim.run()
