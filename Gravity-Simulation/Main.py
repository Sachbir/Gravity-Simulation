import pygame
import sys
from time import time

import config
from Object import Object


class Simulation:

    @staticmethod
    def run():

        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(config.window_size)

        frame_num = 0

        o = Object()

        while True:

            # frame_start_time = time()

            Simulation.event_processing()

            screen.fill((225, 225, 225))

            o.render()

            pygame.display.flip()
            frame_num += 1

            clock.tick(config.UPS_max)
            # Simulation.measure_update_time(frame_start_time)

    @staticmethod
    def event_processing():
        """Checks for any and all events occurring during runtime"""

        if config.frame_counter % 3 == 0:
            for event in pygame.event.get():
                if (event.type == pygame.QUIT or
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_q)):  # End simulation
                    sys.exit(0)

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


Simulation.run()
