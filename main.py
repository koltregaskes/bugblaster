import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bug Blaster")

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
        shoot_sound.play()

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
        self.set_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = 1 # 1 for right, -1 for left
        self.speed = 20
        self.diving = False

    def set_image(self):
        if self.is_head:
            self.image = pygame.image.load('assets/images/centipede_head.png').convert_alpha()
        else:
            self.image = pygame.image.load('assets/images/centipede_body.png').convert_alpha()

    def move_down(self):
        self.rect.y += self.speed
        self.direction *= -1
        if self.is_head:
            collided = pygame.sprite.spritecollide(self, mushrooms, False)
            if collided and collided[0].poisoned:
                self.diving = True

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
all_sprites.add(player)

# Game variables
score = 0
lives = 3
level = 1

# Font for UI
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Sounds
shoot_sound = pygame.mixer.Sound('assets/sounds/shoot.wav')
enemy_hit_sound = pygame.mixer.Sound('assets/sounds/enemy_hit.wav')
player_die_sound = pygame.mixer.Sound('assets/sounds/player_die.wav')

# Create mushrooms
for i in range(50):
    x = random.randrange(0, SCREEN_WIDTH - 20, 20)
    y = random.randrange(50, SCREEN_HEIGHT - 100, 20)
    mushroom = Mushroom(x, y)
    all_sprites.add(mushroom)
    mushrooms.add(mushroom)

# Create centipedes list
centipedes = []

# Create initial centipede
initial_centipede = []
for i in range(12):
    x = (SCREEN_WIDTH // 2) - (i * 20)
    y = 0
    segment = Centipede(x, y, i == 0)
    all_sprites.add(segment)
    centipede_segments.add(segment)
    initial_centipede.append(segment)
centipedes.append(initial_centipede)


# Game loop
running = True
clock = pygame.time.Clock()
frame_counter = 0
CENTIPEDE_SPEED = 5
SPIDER_SPAWN_RATE = 240 # Every 4 seconds (60 * 4)
spider_spawn_counter = 0
FLEA_SPAWN_MUSHROOM_THRESHOLD = 5
SCORPION_SPAWN_RATE = 600 # Every 10 seconds
scorpion_spawn_counter = 0


while running:
    # Keep loop running at the right speed
    clock.tick(60)

    # Spider spawning
    spider_spawn_counter += 1
    if spider_spawn_counter >= SPIDER_SPAWN_RATE and len(spiders) == 0:
        spider_spawn_counter = 0
        spider = Spider()
        all_sprites.add(spider)
        spiders.add(spider)

    # Flea spawning
    mushrooms_in_player_area = [m for m in mushrooms if m.rect.y > SCREEN_HEIGHT / 2]
    if len(mushrooms_in_player_area) < FLEA_SPAWN_MUSHROOM_THRESHOLD and len(fleas) == 0 and random.randint(1, 120) == 1:
        flea = Flea()
        all_sprites.add(flea)
        fleas.add(flea)

    # Scorpion spawning
    scorpion_spawn_counter += 1
    if scorpion_spawn_counter >= SCORPION_SPAWN_RATE and len(scorpions) == 0:
        scorpion_spawn_counter = 0
        scorpion = Scorpion()
        all_sprites.add(scorpion)
        scorpions.add(scorpion)

    # Centipede movement
    frame_counter += 1
    if frame_counter >= CENTIPEDE_SPEED:
        frame_counter = 0
        # Using a copy of the list to allow modification during iteration
        for centipede in list(centipedes):
            if not centipede: # Skip empty centipedes
                centipedes.remove(centipede)
                continue

            # Move body from tail to head
            for i in range(len(centipede) - 1, 0, -1):
                centipede[i].rect.topleft = centipede[i-1].rect.topleft

            # Move head
            head = centipede[0]
            head.rect.x += head.speed * head.direction

            # Collision detection for head
            if head.rect.right > SCREEN_WIDTH or head.rect.left < 0:
                head.move_down()

            collided_mushrooms = pygame.sprite.spritecollide(head, mushrooms, False)
            if collided_mushrooms:
                head.move_down()

    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speed_x = -5
            elif event.key == pygame.K_RIGHT:
                player.speed_x = 5
            elif event.key == pygame.K_SPACE:
                player.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.speed_x = 0

    # Update
    all_sprites.update()

    # Check for bullet-mushroom collisions
    hits = pygame.sprite.groupcollide(bullets, mushrooms, True, False)
    for hit_list in hits.values():
        for mushroom in hit_list:
            score += mushroom.hit()

    # Check for bullet-centipede collisions
    hits = pygame.sprite.groupcollide(bullets, centipede_segments, True, False)
    for bullet, hit_segments in hits.items():
        for segment in hit_segments:
            enemy_hit_sound.play()
            # Create a mushroom where the segment was
            mushroom = Mushroom(segment.rect.x, segment.rect.y)
            all_sprites.add(mushroom)
            mushrooms.add(mushroom)

            # Find the centipede and segment index
            for centipede in list(centipedes):
                if segment in centipede:
                    index = centipede.index(segment)

                    # Award points
                    if segment.is_head:
                        score += 100
                    else:
                        score += 10

                    # Kill the segment
                    segment.kill()

                    # If it's not the tail, promote the next segment to a head
                    if index + 1 < len(centipede):
                        next_segment = centipede[index + 1]
                        next_segment.is_head = True
                        next_segment.set_color()

                        # Split the centipede
                        new_centipede = list(centipede[index + 1:])
                        centipedes.append(new_centipede)

                    # Remove the hit segment and the rest of the original centipede
                    del centipede[index:]

                    # If the original centipede is now empty, remove it
                    if not centipede:
                        centipedes.remove(centipede)

                    break # Move to the next hit segment

    # Check for bullet-spider collisions
    hits = pygame.sprite.groupcollide(bullets, spiders, True, True)
    if hits:
        score += 600
        enemy_hit_sound.play()

    # Check for bullet-flea collisions
    hits = pygame.sprite.groupcollide(bullets, fleas, True, False)
    for hit_list in hits.values():
        for flea in hit_list:
            flea.hit()
            score += 200
            enemy_hit_sound.play()

    # Check for bullet-scorpion collisions
    hits = pygame.sprite.groupcollide(bullets, scorpions, True, True)
    if hits:
        score += 1000
        enemy_hit_sound.play()

    # Check for player collisions
    player_collided = False
    if pygame.sprite.spritecollide(player, centipede_segments, False): player_collided = True
    if pygame.sprite.spritecollide(player, spiders, False): player_collided = True
    if pygame.sprite.spritecollide(player, fleas, False): player_collided = True
    if pygame.sprite.spritecollide(player, scorpions, False): player_collided = True

    if player_collided:
        player_die_sound.play()
        lives -= 1
        if lives <= 0:
            running = False # Game over
        else:
            # Reset player position and clear enemies
            player.rect.x = SCREEN_WIDTH // 2
            for s in list(centipede_segments) + list(spiders) + list(fleas) + list(scorpions):
                s.kill()
            # Brief pause
            pygame.time.wait(1000)
            # Respawn centipede
            initial_centipede = []
            for i in range(12):
                x = (SCREEN_WIDTH // 2) - (i * 20)
                y = 0
                segment = Centipede(x, y, i == 0)
                all_sprites.add(segment)
                centipede_segments.add(segment)
                initial_centipede.append(segment)
            centipedes.append(initial_centipede)


    # Level up
    if not any(centipedes):
        level += 1
        # Clear all enemies and bullets
        for s in list(centipede_segments) + list(spiders) + list(fleas) + list(scorpions) + list(bullets):
            s.kill()

        # Repair a quarter of the mushrooms
        all_mushrooms = mushrooms.sprites()
        random.shuffle(all_mushrooms)
        for i in range(len(all_mushrooms) // 4):
            all_mushrooms[i].health = 4
            all_mushrooms[i].poisoned = False
            all_mushrooms[i].update_color()

        # Brief pause
        pygame.time.wait(1000)

        # Respawn centipede
        initial_centipede = []
        for i in range(12):
            x = (SCREEN_WIDTH // 2) - (i * 20)
            y = 0
            segment = Centipede(x, y, i == 0)
            all_sprites.add(segment)
            centipede_segments.add(segment)
            initial_centipede.append(segment)
        centipedes.append(initial_centipede)
        CENTIPEDE_SPEED = max(1, 5 - level // 3)


    # Draw / render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, SCREEN_WIDTH / 2, 10)
    draw_text(screen, "Lives: " + str(lives), 18, 50, 10)
    draw_text(screen, "Level: " + str(level), 18, SCREEN_WIDTH - 50, 10)


    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()