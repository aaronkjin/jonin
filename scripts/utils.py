import pygame
import os

BASE_IMG_PATH = "data/images/"


def load_image(path):
    # Make more efficient to render
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))

    return img


def load_images(path):
    images = []

    # All files in a given path
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + "/" + img_name))

    return images
