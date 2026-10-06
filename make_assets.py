import os
import math
import wave
import struct
import pygame

pygame.init()

os.makedirs(os.path.join("assets", "images"), exist_ok=True)
os.makedirs(os.path.join("assets", "sounds"), exist_ok=True)

# 1. Basket (Wooden Crate)
basket = pygame.Surface((90, 36), pygame.SRCALPHA)
pygame.draw.rect(basket, (139, 69, 19), (0, 0, 90, 36), border_radius=6)
pygame.draw.rect(basket, (160, 82, 45), (4, 4, 82, 28), border_radius=4)
for x in (25, 45, 65):
    pygame.draw.line(basket, (100, 50, 15), (x, 4), (x, 31), 2)
pygame.image.save(basket, os.path.join("assets", "images", "basket.png"))

# 2. Corn
corn = pygame.Surface((34, 38), pygame.SRCALPHA)
pygame.draw.ellipse(corn, (255, 215, 0), (8, 4, 18, 28))
pygame.draw.polygon(corn, (34, 139, 34), [(6, 26), (17, 36), (8, 36)])
pygame.draw.polygon(corn, (34, 139, 34), [(28, 26), (17, 36), (26, 36)])
pygame.image.save(corn, os.path.join("assets", "images", "corn.png"))

# 3. Egg
egg = pygame.Surface((30, 36), pygame.SRCALPHA)
pygame.draw.ellipse(egg, (245, 238, 220), (3, 3, 24, 30))
pygame.draw.ellipse(egg, (210, 200, 180), (3, 3, 24, 30), 1)
pygame.image.save(egg, os.path.join("assets", "images", "egg.png"))

# 4. Rotten Produce
rotten = pygame.Surface((36, 36), pygame.SRCALPHA)
pygame.draw.circle(rotten, (105, 55, 95), (18, 18), 15)
pygame.draw.circle(rotten, (60, 30, 50), (14, 14), 4)
pygame.draw.circle(rotten, (60, 30, 50), (22, 20), 3)
pygame.image.save(rotten, os.path.join("assets", "images", "rotten.png"))

# 5. Milk Bottle
milk = pygame.Surface((28, 40), pygame.SRCALPHA)
pygame.draw.rect(milk, (240, 240, 240), (4, 10, 20, 28), border_radius=3)
pygame.draw.rect(milk, (70, 130, 180), (8, 4, 12, 6))
pygame.draw.rect(milk, (70, 130, 180), (4, 20, 20, 8))
pygame.image.save(milk, os.path.join("assets", "images", "milk.png"))

# Audio Helper
def make_wav(path, freq1, freq2, duration=0.15):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(n_samples):
            frac = i / n_samples
            freq = freq1 + (freq2 - freq1) * frac
            t = (2.0 * math.pi * freq * i) / sample_rate
            sample = int(math.sin(t) * 16000 * (1.0 - frac))
            f.writeframes(struct.pack('<h', sample))

make_wav(os.path.join("assets", "sounds", "catch.wav"), 440, 880, 0.12)
make_wav(os.path.join("assets", "sounds", "miss.wav"), 280, 120, 0.22)

print("All asset files created successfully inside assets/ folder!")