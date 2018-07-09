import os
import pygame
import time

os.environ['SDL_VIDEO_WINDOW_POS'] = "-590,355"

pygame.init()
screen = pygame.display.set_mode((50, 50), pygame.NOFRAME)


while True:
	screen.fill((255, 255, 0))
	pygame.display.update()