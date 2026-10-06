import sys
import os
import random
import json
import pygame

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

COLOR_SKY = (120, 195, 240)
COLOR_HILL = (85, 145, 95)
COLOR_MEADOW = (55, 120, 60)
COLOR_DIRT = (110, 65, 30)
COLOR_DIRT_LINE = (140, 85, 40)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BROWN = (140, 75, 25)
COLOR_YELLOW = (255, 220, 40)
COLOR_CREAM = (248, 240, 225)
COLOR_PURPLE = (120, 45, 105)
COLOR_GREEN = (60, 210, 80)
COLOR_RED = (235, 55, 65)
COLOR_GOLD = (255, 215, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Harvest")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Arial", 44, bold=True)
font_sub = pygame.font.SysFont("Arial", 22, bold=True)
font_hud = pygame.font.SysFont("Arial", 17, bold=True)
font_body = pygame.font.SysFont("Arial", 18)
font_fx = pygame.font.SysFont("Arial", 20, bold=True)

def load_image(filename, width, height, fallback_color, shape="rect"):
    path = os.path.join("assets", "images", filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (width, height))
        except Exception:
            pass

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    if shape == "circle":
        pygame.draw.circle(surf, fallback_color, (width // 2, height // 2), min(width, height) // 2)
    else:
        pygame.draw.rect(surf, fallback_color, (0, 0, width, height), border_radius=6)
    return surf


def load_sound(filename):
    path = os.path.join("assets", "sounds", filename)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    return None


sound_catch = load_sound("catch.wav")
sound_miss = load_sound("miss.wav")


def play_sound(sound):
    if sound:
        sound.play()

class ScoreManager:
    """Manages persistent high score records using local JSON storage."""
    def __init__(self, filename="scores.json"):
        self.filename = filename
        self.high_score = self.load_record()

    def load_record(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except Exception:
                return 0
        return 0

    def update_record(self, current_score):
        """Saves new record if current score exceeds saved best."""
        is_new_record = False
        if current_score > self.high_score:
            self.high_score = current_score
            is_new_record = True
            try:
                with open(self.filename, "w") as f:
                    json.dump({"high_score": self.high_score}, f, indent=4)
            except Exception as e:
                print(f"Error saving score record: {e}")
        return is_new_record

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-3.5, 1.0)
        self.radius = random.randint(3, 5)
        self.life = 25

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.radius > 1 and self.life % 8 == 0:
            self.radius -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 35

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            rendered = font_fx.render(self.text, True, self.color)
            surface.blit(rendered, (self.x - rendered.get_width() // 2, self.y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 96
        self.height = 38
        self.image = load_image("basket.png", self.width, self.height, COLOR_BROWN, "rect")
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 32
        self.speed = 12

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def reset_position(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 32


class FallingItem(pygame.sprite.Sprite):
    def __init__(self, x, image, speed_y, points, item_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -40
        self.speed_y = speed_y
        self.points = points
        self.item_type = item_type
        self.gravity = 0.05

    def update(self):
        self.speed_y += self.gravity
        self.rect.y += int(self.speed_y)

    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT


class Corn(FallingItem):
    def __init__(self, x, speed_bonus=0):
        img = load_image("corn.png", 34, 38, COLOR_YELLOW, "rect")
        super().__init__(x, img, speed_y=3.2 + speed_bonus, points=10, item_type="harvest")


class Egg(FallingItem):
    def __init__(self, x, speed_bonus=0):
        img = load_image("egg.png", 30, 36, COLOR_CREAM, "circle")
        super().__init__(x, img, speed_y=4.0 + speed_bonus, points=15, item_type="harvest")


class RottenProduce(FallingItem):
    def __init__(self, x, speed_bonus=0):
        img = load_image("rotten.png", 36, 36, COLOR_PURPLE, "circle")
        super().__init__(x, img, speed_y=3.5 + speed_bonus, points=0, item_type="hazard")


class FreshMilk(FallingItem):
    def __init__(self, x, speed_bonus=0):
        img = load_image("milk.png", 28, 40, COLOR_WHITE, "rect")
        super().__init__(x, img, speed_y=4.5 + speed_bonus, points=20, item_type="powerup")


# --- Main Game Engine ---
class Game:
    def __init__(self):
        self.state = "MENU"
        self.player = Player()
        self.items_group = pygame.sprite.Group()
        self.score_manager = ScoreManager()

        self.particles = []
        self.floating_texts = []
        self.clouds = [
            {"x": 60, "y": 60, "speed": 0.4, "radius": 28},
            {"x": 320, "y": 90, "speed": 0.6, "radius": 34},
            {"x": 620, "y": 50, "speed": 0.5, "radius": 24}
        ]

        self.score = 0
        self.lives = 3
        self.combo = 0
        self.level = 1
        self.timer = 60.0
        self.spawn_timer = 0
        self.spawn_interval = 40
        self.is_new_high_score = False

    def start_game(self):
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.level = 1
        self.timer = 60.0
        self.spawn_timer = 0
        self.spawn_interval = 40
        self.is_new_high_score = False
        self.items_group.empty()
        self.particles.clear()
        self.floating_texts.clear()
        self.player.reset_position()
        self.state = "PLAYING"

    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def add_floating_text(self, text, x, y, color):
        self.floating_texts.append(FloatingText(text, x, y, color))

    def spawn_item(self):
        x = random.randint(40, SCREEN_WIDTH - 60)
        speed_bonus = (self.level - 1) * 0.85
        roll = random.random()

        if roll < 0.45:
            item = Corn(x, speed_bonus)
        elif roll < 0.74:
            item = Egg(x, speed_bonus)
        elif roll < 0.91:
            item = RottenProduce(x, speed_bonus)
        else:
            item = FreshMilk(x, speed_bonus)

        self.items_group.add(item)

    def check_progression(self):
        if self.timer > 40:
            self.level = 1
            self.spawn_interval = 40
        elif self.timer > 20:
            self.level = 2
            self.spawn_interval = 30
        else:
            self.level = 3
            self.spawn_interval = 20

    def update_environment(self):
        for c in self.clouds:
            c["x"] += c["speed"]
            if c["x"] - c["radius"] * 2 > SCREEN_WIDTH:
                c["x"] = -c["radius"] * 2
                c["y"] = random.randint(40, 110)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)

    def finalize_match(self, new_state):
        self.state = new_state
        self.is_new_high_score = self.score_manager.update_record(self.score)

    def update_gameplay(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.finalize_match("VICTORY")
            return

        if self.lives <= 0:
            self.finalize_match("GAME_OVER")
            return

        self.check_progression()

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_item()

        self.player.update()
        self.items_group.update()
        self.update_environment()

        for item in list(self.items_group):
            if item.is_off_screen():
                if item.item_type == "harvest":
                    self.lives -= 1
                    self.combo = 0
                    play_sound(sound_miss)
                    self.add_floating_text("-1 LIFE (DROPPED)", item.rect.centerx, SCREEN_HEIGHT - 65, COLOR_RED)
                item.kill()

        hits = pygame.sprite.spritecollide(self.player, self.items_group, True)
        for item in hits:
            cx, cy = item.rect.centerx, item.rect.centery
            if item.item_type == "harvest":
                self.combo += 1
                combo_bonus = (self.combo // 4) * 5
                total_gain = item.points + combo_bonus
                self.score += total_gain
                play_sound(sound_catch)
                self.add_particles(cx, cy, COLOR_YELLOW if isinstance(item, Corn) else COLOR_CREAM)
                label = f"+{total_gain}" if combo_bonus == 0 else f"+{total_gain} ({self.combo}x STREAK!)"
                self.add_floating_text(label, cx, cy - 10, COLOR_YELLOW)

            elif item.item_type == "hazard":
                self.lives -= 1
                self.combo = 0
                play_sound(sound_miss)
                self.add_particles(cx, cy, COLOR_PURPLE, count=16)
                self.add_floating_text("-1 LIFE!", cx, cy - 10, COLOR_RED)

            elif item.item_type == "powerup":
                if self.lives < 5:
                    self.lives += 1
                self.score += item.points
                play_sound(sound_catch)
                self.add_particles(cx, cy, COLOR_WHITE, count=14)
                self.add_floating_text("+1 EXTRA LIFE!", cx, cy - 10, COLOR_GREEN)

    def draw_scenery(self):
        screen.fill(COLOR_SKY)
        for c in self.clouds:
            cx, cy, r = int(c["x"]), int(c["y"]), c["radius"]
            pygame.draw.circle(screen, (245, 250, 255), (cx, cy), r)
            pygame.draw.circle(screen, (245, 250, 255), (cx + r - 8, cy - 6), int(r * 0.8))
            pygame.draw.circle(screen, (245, 250, 255), (cx - r + 8, cy - 4), int(r * 0.75))

        pygame.draw.ellipse(screen, COLOR_HILL, (-80, 290, 520, 360))
        pygame.draw.ellipse(screen, COLOR_HILL, (340, 270, 560, 380))
        pygame.draw.rect(screen, COLOR_MEADOW, (0, 430, SCREEN_WIDTH, 170))
        pygame.draw.line(screen, (80, 160, 85), (0, 430), (SCREEN_WIDTH, 430), 3)
        pygame.draw.rect(screen, COLOR_DIRT, (0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32))
        pygame.draw.line(screen, COLOR_DIRT_LINE, (0, SCREEN_HEIGHT - 32), (SCREEN_WIDTH, SCREEN_HEIGHT - 32), 4)

    def draw_hud(self):
        bar = pygame.Surface((SCREEN_WIDTH, 48), pygame.SRCALPHA)
        bar.fill((20, 35, 25, 215))
        screen.blit(bar, (0, 0))

        hearts = " ".join(["♥" for _ in range(self.lives)])
        score_surf = font_hud.render(f"SCORE: {self.score}", True, COLOR_YELLOW)
        hi_surf = font_hud.render(f"HIGH: {self.score_manager.high_score}", True, COLOR_GOLD)
        lives_surf = font_hud.render(f"LIVES: {hearts}", True, COLOR_RED if self.lives == 1 else COLOR_WHITE)
        streak_surf = font_hud.render(f"STREAK: {self.combo}x", True, COLOR_GREEN if self.combo >= 4 else (180, 200, 190))
        time_surf = font_hud.render(f"TIME: {int(self.timer)}s", True, COLOR_WHITE)

        screen.blit(score_surf, (15, 14))
        screen.blit(hi_surf, (140, 14))
        screen.blit(lives_surf, (275, 14))
        screen.blit(streak_surf, (460, 14))
        screen.blit(time_surf, (685, 14))

    def draw_menu(self):
        self.draw_scenery()
        card = pygame.Surface((560, 380), pygame.SRCALPHA)
        card.fill((15, 28, 18, 225))
        card_rect = card.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(card, card_rect)
        pygame.draw.rect(screen, COLOR_YELLOW, card_rect, width=3, border_radius=12)

        title = font_title.render("FARM HARVEST", True, COLOR_YELLOW)
        hi_text = font_sub.render(f"BEST RECORD: {self.score_manager.high_score}", True, COLOR_GOLD)
        start_txt = font_sub.render("[ENTER] Start Harvest", True, COLOR_WHITE)
        inst_txt = font_sub.render("[I] Farmer's Guide & Rules", True, (255, 235, 140))
        exit_txt = font_sub.render("[ESC] Exit Game", True, COLOR_RED)

        cx = SCREEN_WIDTH // 2
        screen.blit(title, title.get_rect(center=(cx, 165)))
        screen.blit(hi_text, hi_text.get_rect(center=(cx, 215)))
        screen.blit(start_txt, start_txt.get_rect(center=(cx, 275)))
        screen.blit(inst_txt, inst_txt.get_rect(center=(cx, 325)))
        screen.blit(exit_txt, exit_txt.get_rect(center=(cx, 375)))

    def draw_instructions(self):
        self.draw_scenery()
        card = pygame.Surface((640, 480), pygame.SRCALPHA)
        card.fill((15, 28, 18, 235))
        card_rect = card.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(card, card_rect)
        pygame.draw.rect(screen, COLOR_YELLOW, card_rect, width=3, border_radius=12)

        lines = [
            ("FARMER'S GUIDE & RULES", font_title, COLOR_YELLOW),
            ("Move Basket: LEFT / RIGHT Arrows or A / D keys", font_body, COLOR_WHITE),
            ("Catch Sweet Corn (+10 pts) and Fresh Eggs (+15 pts)", font_body, COLOR_WHITE),
            ("Missing/Dropping crops costs 1 Life!", font_body, COLOR_RED),
            ("Avoid Rotten Produce! Catching it costs 1 Life", font_body, COLOR_RED),
            ("Fresh Milk bottles restore 1 Lost Life", font_body, COLOR_GREEN),
            ("Build Streaks (4x, 8x...) for huge bonus scores", font_body, COLOR_YELLOW),
            ("Controls: [P] Pause | [R] Restart anytime", font_body, (180, 210, 240)),
            ("Survive the full 60 seconds to WIN!", font_body, COLOR_WHITE),
            ("Press [ENTER] or [ESC] to Return to Menu", font_sub, COLOR_YELLOW)
        ]
        y = 90
        for text, font, color in lines:
            rendered = font.render(text, True, color)
            screen.blit(rendered, rendered.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 38

    def draw_overlay(self, title_text, color, subtitle_text):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        t1 = font_title.render(title_text, True, color)
        t2 = font_sub.render(subtitle_text, True, COLOR_WHITE)
        screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
        screen.blit(t2, t2.get_rect(center=(cx, cy + 15)))

        if self.is_new_high_score:
            record_txt = font_sub.render("CONGRATULATIONS! NEW HIGH SCORE!", True, COLOR_GOLD)
            screen.blit(record_txt, record_txt.get_rect(center=(cx, cy + 65)))

    def render(self):
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "INSTRUCTIONS":
            self.draw_instructions()
        else:
            self.draw_scenery()
            screen.blit(self.player.image, self.player.rect)
            self.items_group.draw(screen)

            for p in self.particles:
                p.draw(screen)
            for ft in self.floating_texts:
                ft.draw(screen)

            self.draw_hud()

            if self.state == "PAUSED":
                self.draw_overlay("GAME PAUSED", COLOR_YELLOW, "Press [P] to Resume | [R] to Restart")
            elif self.state == "GAME_OVER":
                self.draw_overlay("HARVEST FAILED", COLOR_RED, f"Final Score: {self.score} | Press [R] to Retry")
            elif self.state == "VICTORY":
                self.draw_overlay("SUCCESSFUL HARVEST!", COLOR_GREEN, f"Final Score: {self.score} | Press [R] to Replay")

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.state == "MENU":
                        if event.key == pygame.K_RETURN:
                            self.start_game()
                        elif event.key == pygame.K_i:
                            self.state = "INSTRUCTIONS"
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                    elif self.state == "INSTRUCTIONS":
                        if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                            self.state = "MENU"

                    elif self.state == "PLAYING":
                        if event.key == pygame.K_p:
                            self.state = "PAUSED"
                        elif event.key == pygame.K_r:
                            self.start_game()

                    elif self.state == "PAUSED":
                        if event.key == pygame.K_p:
                            self.state = "PLAYING"
                        elif event.key == pygame.K_r:
                            self.start_game()

                    elif self.state in ("GAME_OVER", "VICTORY"):
                        if event.key == pygame.K_r:
                            self.start_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "MENU"

            if self.state == "PLAYING":
                self.update_gameplay(dt)
            elif self.state in ("MENU", "INSTRUCTIONS"):
                self.update_environment()

            self.render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()