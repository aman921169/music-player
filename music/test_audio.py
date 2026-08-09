import pygame
import time

pygame.mixer.init()

pygame.mixer.music.load("test.mp3")
pygame.mixer.music.play()

print("Playing music...")

while pygame.mixer.music.get_busy():
    time.sleep(1)

print("Finished!")