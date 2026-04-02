import random
import os
import json

import pygame


class SilentSound:
    def play(self):
        return None

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False

HEADLESS_SMOKE_TEST = os.environ.get("BUGBLASTER_HEADLESS_SMOKE_TEST") == "1"
SMOKE_TEST_FRAME_LIMIT = 120

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Swarmbreaker")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/images/player.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - 50
        self.speed_x = 0

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        play_sound(shoot_sound)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([5, 10])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Mushroom class
class Mushroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.image.load('assets/images/mushroom.png').convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 4
        self.poisoned = False
        self.update_color()

    def hit(self):
        self.health -= 1
        points = 1
        if self.health <= 0:
            self.kill()
            points += 5
        else:
            self.update_color()
        return points

    def poison(self):
        if not self.poisoned:
            self.poisoned = True
            self.update_color()

    def update_color(self):
        if self.poisoned:
            if self.health == 4: self.image.fill((128, 0, 128)) # Purple
            elif self.health == 3: self.image.fill((148, 0, 211))
            elif self.health == 2: self.image.fill((153, 50, 204))
            elif self.health == 1: self.image.fill((186, 85, 211))
        else:
            if self.health == 4: self.image.fill(WHITE)
            elif self.health == 3: self.image.fill((255, 255, 0)) # Yellow
            elif self.health == 2: self.image.fill((255, 165, 0)) # Orange
            elif self.health == 1: self.image.fill((255, 0, 0)) # Red

# Centipede class
class Centipede(pygame.sprite.Sprite):
    def __init__(self, x, y, is_head=False):
        super().__init__()
        self.is_head = is_head
        self.diving = False
        self.set_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = 1 # 1 for right, -1 for left
        self.speed = 20

    def set_image(self):
        if self.is_head:
            self.image = pygame.image.load('assets/images/centipede_head.png').convert_alpha()
        else:
            self.image = pygame.image.load('assets/images/centipede_body.png').convert_alpha()

        if self.diving and self.is_head:
            self.image = self.image.copy()
            self.image.fill((210, 70, 255, 90), special_flags=pygame.BLEND_RGBA_ADD)

    def move_down(self):
        self.rect.y += self.speed
        self.direction *= -1
        if self.is_head:
            collided = pygame.sprite.spritecollide(self, mushrooms, False)
            if collided and collided[0].poisoned:
                self.diving = True
                self.set_image()

    def move_dive(self):
        self.rect.y += self.speed
        dive_floor = SCREEN_HEIGHT - 120
        if self.rect.top >= dive_floor:
            self.rect.top = dive_floor
            self.diving = False
            self.direction = random.choice([-1, 1])
            self.set_image()

# Spider class
class Spider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/images/spider.png').convert_alpha()
        self.rect = self.image.get_rect()

        # Start off screen
        if random.choice([True, False]):
            self.rect.x = -self.rect.width
            self.speed_x = 3
        else:
            self.rect.x = SCREEN_WIDTH
            self.speed_x = -3

        self.rect.y = random.randrange(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 80)
        self.speed_y = random.choice([-3, 3])
        self.top_boundary = SCREEN_HEIGHT - 200
        self.bottom_boundary = SCREEN_HEIGHT - 50

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top < self.top_boundary or self.rect.bottom > self.bottom_boundary:
            self.speed_y *= -1

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Flea class
class Flea(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/images/flea.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - 20, 20)
        self.rect.y = 0
        self.speed_y = 4
        self.health = 2
        self.last_mushroom_y = 0

    def update(self):
        self.rect.y += self.speed_y
        # Drop mushrooms
        if self.rect.y - self.last_mushroom_y > 20:
             # Only drop if no mushroom is already there
            if not pygame.sprite.spritecollide(self, mushrooms, False):
                mushroom = Mushroom(self.rect.x, self.rect.y)
                all_sprites.add(mushroom)
                mushrooms.add(mushroom)
            self.last_mushroom_y = self.rect.y

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

# Scorpion class
class Scorpion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/images/scorpion.png').convert_alpha()
        self.rect = self.image.get_rect()

        if random.choice([True, False]):
            self.rect.x = -self.rect.width
            self.speed_x = 2
        else:
            self.rect.x = SCREEN_WIDTH
            self.speed_x = -2

        self.rect.y = random.randrange(50, SCREEN_HEIGHT // 2)

    def update(self):
        self.rect.x += self.speed_x

        # Poison mushrooms
        collided_mushrooms = pygame.sprite.spritecollide(self, mushrooms, False)
        for mushroom in collided_mushrooms:
            mushroom.poison()

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


# Sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
mushrooms = pygame.sprite.Group()
centipede_segments = pygame.sprite.Group()
spiders = pygame.sprite.Group()
fleas = pygame.sprite.Group()
scorpions = pygame.sprite.Group()

player = Player()

font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_centered_lines(lines, start_y, size=22, color=WHITE, line_gap=28):
    for index, line in enumerate(lines):
        draw_text(screen, line, size, SCREEN_WIDTH / 2, start_y + index * line_gap, color)


def load_sound(path):
    if not AUDIO_AVAILABLE:
        return SilentSound()

    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return SilentSound()


shoot_sound = load_sound('assets/sounds/shoot.wav')
enemy_hit_sound = load_sound('assets/sounds/enemy_hit.wav')
player_die_sound = load_sound('assets/sounds/player_die.wav')

HIGH_SCORE_PATH = 'swarmbreaker_highscore.json'
TITLE_COLOR = (86, 220, 255)
PANEL_COLOR = (16, 20, 30)
PANEL_BORDER = (50, 85, 120)
SUCCESS_COLOR = (112, 235, 157)
WARNING_COLOR = (255, 204, 94)
EXTRA_LIFE_STEP = 10000
AUDIO_ON_COLOR = (132, 232, 179)
AUDIO_OFF_COLOR = (255, 160, 160)

score = 0
lives = 3
level = 1
high_score = 0
game_phase = 'title'
centipedes = []
next_extra_life_score = EXTRA_LIFE_STEP
status_message = ''
status_timer = 0
sound_enabled = AUDIO_AVAILABLE

running = True
clock = pygame.time.Clock()
frame_counter = 0
smoke_test_frames = 0
CENTIPEDE_SPEED = 5
SPIDER_SPAWN_RATE = 240
spider_spawn_counter = 0
FLEA_SPAWN_MUSHROOM_THRESHOLD = 5
SCORPION_SPAWN_RATE = 600
scorpion_spawn_counter = 0


def load_high_score():
    try:
        with open(HIGH_SCORE_PATH, 'r', encoding='utf-8') as file:
            return int(json.load(file).get('high_score', 0))
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_PATH, 'w', encoding='utf-8') as file:
            json.dump({'high_score': int(value)}, file)
    except OSError:
        pass


def set_status_message(message, frames=150):
    global status_message, status_timer
    status_message = message
    status_timer = frames


def play_sound(sound):
    if sound_enabled:
        sound.play()


def toggle_sound():
    global sound_enabled
    if not AUDIO_AVAILABLE:
        set_status_message('Audio device unavailable on this machine.', 180)
        return

    sound_enabled = not sound_enabled
    if sound_enabled:
        set_status_message('Audio restored.', 150)
    else:
        set_status_message('Audio muted.', 150)


def award_points(points):
    global score, high_score, lives, next_extra_life_score
    score += points
    high_score = max(high_score, score)
    while score >= next_extra_life_score:
        lives += 1
        set_status_message('Bonus life awarded!', 180)
        next_extra_life_score += EXTRA_LIFE_STEP


def spawn_centipede_wave(length=12):
    global centipedes
    new_centipede = []
    for i in range(length):
        x = (SCREEN_WIDTH // 2) - (i * 20)
        y = 0
        segment = Centipede(x, y, i == 0)
        all_sprites.add(segment)
        centipede_segments.add(segment)
        new_centipede.append(segment)
    centipedes.append(new_centipede)


def build_mushroom_field(count=50):
    for _ in range(count):
        x = random.randrange(0, SCREEN_WIDTH - 20, 20)
        y = random.randrange(50, SCREEN_HEIGHT - 100, 20)
        mushroom = Mushroom(x, y)
        all_sprites.add(mushroom)
        mushrooms.add(mushroom)


def clear_enemies(include_mushrooms=False):
    groups = [bullets, centipede_segments, spiders, fleas, scorpions]
    if include_mushrooms:
        groups.append(mushrooms)

    for group in groups:
        for sprite in list(group):
            sprite.kill()


def start_new_game():
    global score, lives, level, game_phase, CENTIPEDE_SPEED, spider_spawn_counter
    global scorpion_spawn_counter, frame_counter, centipedes, next_extra_life_score
    all_sprites.empty()
    bullets.empty()
    mushrooms.empty()
    centipede_segments.empty()
    spiders.empty()
    fleas.empty()
    scorpions.empty()
    centipedes = []

    score = 0
    lives = 3
    level = 1
    next_extra_life_score = EXTRA_LIFE_STEP
    CENTIPEDE_SPEED = 5
    spider_spawn_counter = 0
    scorpion_spawn_counter = 0
    frame_counter = 0
    player.rect.x = SCREEN_WIDTH // 2
    player.rect.y = SCREEN_HEIGHT - 50
    player.speed_x = 0
    all_sprites.add(player)
    build_mushroom_field()
    spawn_centipede_wave()
    game_phase = 'playing'
    set_status_message('Wave 1 deployed. Hold the line.', 180)


def reset_after_life():
    global centipedes
    clear_enemies()
    centipedes = []
    player.rect.x = SCREEN_WIDTH // 2
    player.rect.y = SCREEN_HEIGHT - 50
    player.speed_x = 0
    spawn_centipede_wave()
    set_status_message('Defence line restored.', 150)


def advance_level():
    global level, CENTIPEDE_SPEED, centipedes
    level += 1
    clear_enemies()
    centipedes = []
    all_mushrooms = mushrooms.sprites()
    random.shuffle(all_mushrooms)
    for mushroom in all_mushrooms[: max(1, len(all_mushrooms) // 4)]:
        mushroom.health = 4
        mushroom.poisoned = False
        mushroom.update_color()
    spawn_centipede_wave(min(12 + (level - 1), 18))
    CENTIPEDE_SPEED = max(1, 5 - level // 3)
    set_status_message(f'Wave {level} incoming.', 180)


def enter_game_over():
    global game_phase, high_score
    game_phase = 'game_over'
    high_score = max(high_score, score)
    save_high_score(high_score)


def draw_panel():
    panel_rect = pygame.Rect(80, 70, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 140)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=16)
    pygame.draw.rect(screen, PANEL_BORDER, panel_rect, width=2, border_radius=16)


def draw_title_screen():
    screen.fill((8, 10, 16))
    draw_panel()
    draw_text(screen, 'SWARMBREAKER', 48, SCREEN_WIDTH / 2, 120, TITLE_COLOR)
    draw_centered_lines(
        [
            'Retro arcade defence against an endless segmented swarm.',
            'Clear centipedes, dodge spiders and fleas, and survive as long as you can.',
            'Poisoned mushrooms force centipede heads into a direct dive through your line.',
        ],
        205,
        18,
        (215, 223, 237),
        28,
    )
    draw_centered_lines(
        [
            'Controls',
            'Arrow Keys  Move',
            'Space       Fire',
            'P           Pause',
            'M           Mute Audio',
            'Enter       Start',
            'Esc         Quit',
        ],
        305,
        18,
        WHITE,
        24,
    )
    draw_text(screen, f'High Score  {high_score}', 22, SCREEN_WIDTH / 2, 455, (255, 204, 94))
    draw_text(screen, 'Every 10,000 points earns an extra life.', 18, SCREEN_WIDTH / 2, 485, SUCCESS_COLOR)
    audio_color = AUDIO_ON_COLOR if sound_enabled else AUDIO_OFF_COLOR
    audio_label = 'Audio On' if sound_enabled else 'Audio Muted'
    draw_text(screen, audio_label, 18, SCREEN_WIDTH / 2, 515, audio_color)
    draw_text(screen, 'Press Enter to begin the next defence line.', 18, SCREEN_WIDTH / 2, 545, (180, 190, 210))


def draw_game_over_screen():
    screen.fill((8, 10, 16))
    draw_panel()
    draw_text(screen, 'DEFENCE LINE LOST', 40, SCREEN_WIDTH / 2, 140, (255, 110, 110))
    draw_text(screen, f'Score  {score}', 28, SCREEN_WIDTH / 2, 235, WHITE)
    draw_text(screen, f'Level Reached  {level}', 24, SCREEN_WIDTH / 2, 275, TITLE_COLOR)
    draw_text(screen, f'High Score  {high_score}', 24, SCREEN_WIDTH / 2, 315, (255, 204, 94))
    draw_centered_lines(
        [
            'Press Enter to deploy again.',
            'Press M to toggle audio.',
            'Press Esc to stand down.',
        ],
        395,
        18,
        (180, 190, 210),
        26,
    )


def draw_hud():
    draw_text(screen, f'Score: {score}', 18, SCREEN_WIDTH / 2, 10)
    draw_text(screen, f'Lives: {lives}', 18, 70, 10)
    draw_text(screen, f'Level: {level}', 18, SCREEN_WIDTH - 70, 10)
    draw_text(screen, f'High: {high_score}', 16, SCREEN_WIDTH / 2, 34, (255, 204, 94))
    draw_text(screen, f'Next Life: {next_extra_life_score}', 14, SCREEN_WIDTH - 110, 34, SUCCESS_COLOR)
    audio_label = 'Audio On' if sound_enabled else 'Audio Muted'
    audio_color = AUDIO_ON_COLOR if sound_enabled else AUDIO_OFF_COLOR
    draw_text(screen, audio_label, 14, 110, 34, audio_color)


def draw_status_banner():
    if status_timer <= 0 or not status_message:
        return

    banner = pygame.Rect(215, 58, SCREEN_WIDTH - 430, 34)
    pygame.draw.rect(screen, PANEL_COLOR, banner, border_radius=10)
    pygame.draw.rect(screen, PANEL_BORDER, banner, width=1, border_radius=10)
    draw_text(screen, status_message, 16, SCREEN_WIDTH / 2, 64, WARNING_COLOR)


def draw_pause_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 8, 16, 150))
    screen.blit(overlay, (0, 0))
    draw_panel()
    draw_text(screen, 'PAUSED', 42, SCREEN_WIDTH / 2, 170, TITLE_COLOR)
    draw_centered_lines(
        [
            'Press P to resume the defence line.',
            'Press M to mute or restore the arcade mix.',
            'Press Esc if you want to abandon this run.',
        ],
        285,
        20,
        (215, 223, 237),
        30,
    )


high_score = load_high_score()
if HEADLESS_SMOKE_TEST:
    start_new_game()

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                toggle_sound()
            if event.key == pygame.K_ESCAPE:
                if game_phase == 'playing':
                    enter_game_over()
                elif game_phase == 'paused':
                    enter_game_over()
                else:
                    running = False
            elif game_phase in ('title', 'game_over'):
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_new_game()
            elif game_phase == 'playing':
                if event.key == pygame.K_LEFT:
                    player.speed_x = -5
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = 5
                elif event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_p:
                    player.speed_x = 0
                    game_phase = 'paused'
                    set_status_message('Run paused.', 120)
            elif game_phase == 'paused' and event.key == pygame.K_p:
                game_phase = 'playing'
                set_status_message('Back in the fight.', 120)
        elif event.type == pygame.KEYUP and game_phase == 'playing':
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player.speed_x = 0

    if game_phase == 'title':
        draw_title_screen()
        pygame.display.flip()
        continue

    if game_phase == 'game_over':
        draw_game_over_screen()
        pygame.display.flip()
        continue

    if game_phase == 'paused':
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_hud()
        draw_pause_overlay()
        pygame.display.flip()
        continue

    spider_spawn_counter += 1
    if spider_spawn_counter >= SPIDER_SPAWN_RATE and len(spiders) == 0:
        spider_spawn_counter = 0
        spider = Spider()
        all_sprites.add(spider)
        spiders.add(spider)

    mushrooms_in_player_area = [m for m in mushrooms if m.rect.y > SCREEN_HEIGHT / 2]
    if len(mushrooms_in_player_area) < FLEA_SPAWN_MUSHROOM_THRESHOLD and len(fleas) == 0 and random.randint(1, 120) == 1:
        flea = Flea()
        all_sprites.add(flea)
        fleas.add(flea)

    scorpion_spawn_counter += 1
    if scorpion_spawn_counter >= SCORPION_SPAWN_RATE and len(scorpions) == 0:
        scorpion_spawn_counter = 0
        scorpion = Scorpion()
        all_sprites.add(scorpion)
        scorpions.add(scorpion)

    frame_counter += 1
    if frame_counter >= CENTIPEDE_SPEED:
        frame_counter = 0
        for centipede in list(centipedes):
            if not centipede:
                centipedes.remove(centipede)
                continue

            for i in range(len(centipede) - 1, 0, -1):
                centipede[i].rect.topleft = centipede[i - 1].rect.topleft

            head = centipede[0]
            if head.diving:
                head.move_dive()
            else:
                head.rect.x += head.speed * head.direction

                if head.rect.right > SCREEN_WIDTH or head.rect.left < 0:
                    head.move_down()

                if pygame.sprite.spritecollide(head, mushrooms, False):
                    head.move_down()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(bullets, mushrooms, True, False)
    for hit_list in hits.values():
        for mushroom in hit_list:
            award_points(mushroom.hit())

    hits = pygame.sprite.groupcollide(bullets, centipede_segments, True, False)
    for hit_segments in hits.values():
        for segment in hit_segments:
            play_sound(enemy_hit_sound)
            mushroom = Mushroom(segment.rect.x, segment.rect.y)
            all_sprites.add(mushroom)
            mushrooms.add(mushroom)

            for centipede in list(centipedes):
                if segment in centipede:
                    index = centipede.index(segment)
                    award_points(100 if segment.is_head else 10)
                    segment.kill()

                    if index + 1 < len(centipede):
                        next_segment = centipede[index + 1]
                        next_segment.is_head = True
                        next_segment.set_image()
                        centipedes.append(list(centipede[index + 1:]))

                    del centipede[index:]
                    if not centipede:
                        centipedes.remove(centipede)
                    break

    hits = pygame.sprite.groupcollide(bullets, spiders, True, True)
    if hits:
        award_points(600)
        play_sound(enemy_hit_sound)

    hits = pygame.sprite.groupcollide(bullets, fleas, True, False)
    for hit_list in hits.values():
        for flea in hit_list:
            flea.hit()
            award_points(200)
            play_sound(enemy_hit_sound)

    hits = pygame.sprite.groupcollide(bullets, scorpions, True, True)
    if hits:
        award_points(1000)
        play_sound(enemy_hit_sound)

    player_collided = any(
        pygame.sprite.spritecollide(player, group, False)
        for group in (centipede_segments, spiders, fleas, scorpions)
    )

    if player_collided:
        play_sound(player_die_sound)
        lives -= 1
        if lives <= 0:
            enter_game_over()
        else:
            pygame.time.wait(500)
            reset_after_life()

    if not centipedes:
        pygame.time.wait(400)
        advance_level()

    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_hud()
    draw_status_banner()
    pygame.display.flip()

    if status_timer > 0:
        status_timer -= 1
        if status_timer == 0:
            status_message = ''

    if HEADLESS_SMOKE_TEST:
        smoke_test_frames += 1
        if smoke_test_frames >= SMOKE_TEST_FRAME_LIMIT:
            running = False

save_high_score(max(high_score, score))
pygame.quit()
