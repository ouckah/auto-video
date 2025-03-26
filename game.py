import pygame
import cv2
import time
from recorder import Recorder
from games.squares_fight import SquareFight
from util import get_window_position

pygame.init()

# game variables
WINDOW_NAME = "Python"
FPS = 60
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1016

# set up Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption(WINDOW_NAME)

# force window creation by handling a few events
for _ in range(5):  # process a few events to ensure window is initialized
    pygame.event.get()
    pygame.display.flip()

def game_loop(game, fps):
    clock = pygame.time.Clock()
    start_time = time.time()
    game.start()

    while True:
        game.update()  # update game state
        pygame.display.flip()  # update display
        if RECORD_MODE == "timed" and time.time() - start_time >= VIDEO_LENGTH:  # stop after VIDEO_LENGTH seconds
            break
        if RECORD_MODE == "signal" and game.playing() == False:
            end_signal_time = time.time()

            # continue for 3 more seconds
            while time.time() - end_signal_time < 3:
                game.update()
                pygame.display.flip()
                clock.tick(fps)
                
            break
        clock.tick(fps)

# recording setup
RECORD_MODE = "signal" # "signal" or "timed"
VIDEO_LENGTH = 5 # in seconds (for "timed" mode)
FOURCC = "mp4v"
OUTPUT_FILE = "output.mp4"
recorder = Recorder(fourcc=FOURCC, fps=FPS, output_file=OUTPUT_FILE)
game = SquareFight(screen, fps=FPS, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

if __name__ == "__main__":
    time.sleep(0.5)
    
    # get window-to-be-recorded data
    x, y, width, height = get_window_position(WINDOW_NAME)
    print(x, y, width, height)
    
    # start recording window
    recorder.start_recording(x, y, width, height)

    # run the game loop in the main thread
    game_loop(game, FPS)

    # end recording
    recorder.stop_recording()

# cleanup
pygame.quit()
cv2.destroyAllWindows()
