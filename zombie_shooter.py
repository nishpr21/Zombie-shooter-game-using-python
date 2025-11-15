import pygame, random, os, sys, time

pygame.init()

# Fullscreen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Zombie Shooter")

clock = pygame.time.Clock()
FPS = 30

# Load sounds
shoot_sound = pygame.mixer.Sound("assets/sounds/gun-shot-359196.mp3")
game_over_sound = pygame.mixer.Sound("assets/sounds/sfx-defeat3.mp3")

# Load background
background = pygame.image.load("assets/zombie_img.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Function to load animation frames 
def load_animation(path, scale=(120, 120), flip=False):
    frames = []
    for file in sorted(os.listdir(path)):
        if file.endswith(".png"):
            img = pygame.image.load(os.path.join(path, file)).convert_alpha()
            img = pygame.transform.scale(img, scale)
            if flip:
                img = pygame.transform.flip(img, True, False)  # flip horizontally
            frames.append(img)
    return frames

# Player animations
player_idle = load_animation("assets/player/idle", scale=(120, 120))
player_walk = load_animation("assets/player/walk", scale=(120, 120))
player_attack = load_animation("assets/player/attack", scale=(120, 120))
player_death = load_animation("assets/player/death", scale=(120, 120))

# Zombie animations 
zombie_idle = load_animation("assets/zombies/idle", scale=(100, 100), flip=True)
zombie_walk = load_animation("assets/zombies/walk", scale=(100, 100), flip=True)
zombie_attack = load_animation("assets/zombies/attack", scale=(100, 100), flip=True)
zombie_death = load_animation("assets/zombies/death", scale=(100, 100), flip=True)

# Displaying Highest Score of all time
def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

highscore = load_highscore()


# Classes
class Player:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.health = 5
        self.animation = player_idle
        self.frame = 0
        self.image = self.animation[self.frame]
        self.alive = True
        self.speed = 7
        self.shooting = False

    def update(self, keys):
        if not self.alive:
            self.animation = player_death
        else:
            moved = False
            if keys[pygame.K_RIGHT] and self.x < WIDTH - 150:
                self.animation = player_walk
                self.x += self.speed
                moved = True
            if keys[pygame.K_LEFT] and self.x > 50:
                self.animation = player_walk
                self.x -= self.speed
                moved = True
            if keys[pygame.K_UP] and self.y > 50:
                self.animation = player_walk
                self.y -= self.speed
                moved = True
            if keys[pygame.K_DOWN] and self.y < HEIGHT - 150:
                self.animation = player_walk
                self.y += self.speed
                moved = True
            if keys[pygame.K_SPACE]:
                self.animation = player_attack
                self.shooting = True
                if self.frame == 0:  # play sound once per attack cycle
                    shoot_sound.play()
            else:
                self.shooting = False
                if not moved:
                    self.animation = player_idle

        self.frame = (self.frame + 1) % len(self.animation)
        self.image = self.animation[self.frame]

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        # health bar for player
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, 40 * self.health, 20))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

class Zombie:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(HEIGHT//2 - 200, HEIGHT - 150)
        self.max_health = 3
        self.health = self.max_health
        self.animation = zombie_walk
        self.frame = 0
        self.image = self.animation[self.frame]
        self.alive = True

    def update(self, player):
        if self.alive:
            self.x -= 3
            if self.x < player.x + 80:
                self.animation = zombie_attack
            else:
                self.animation = zombie_walk

            self.frame = (self.frame + 1) % len(self.animation)
            self.image = self.animation[self.frame]

            if self.health <= 0:
                self.alive = False

    def draw(self):
        if self.alive:
            screen.blit(self.image, (self.x, self.y))
            # health bar above zombie
            bar_width = 60
            bar_height = 8
            fill = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y + 40  
        self.speed = 15
        self.alive = True

    def update(self):
        self.x += self.speed
        if self.x > WIDTH:
            self.alive = False

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, 15, 5))

    def rect(self):
        return pygame.Rect(self.x, self.y, 15, 5)

# function to render outlined text
def render_text(text, font, main_color, outline_color, pos):
    base = font.render(text, True, main_color)
    outline = font.render(text, True, outline_color)
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        screen.blit(outline, (pos[0]+dx, pos[1]+dy))
    screen.blit(base, pos)

# Game Over screen
def game_over_screen(score):
    global highscore
    font = pygame.font.SysFont("arialblack", 80, bold=True)
    small_font = pygame.font.SysFont("arialblack", 40, bold=True)

    if score > highscore:
        highscore = score
        save_highscore(highscore)

    while True:
        screen.blit(background, (0, 0))
        render_text("GAME OVER", font, (255, 50, 50), (0, 0, 0), (WIDTH//2 - 200, HEIGHT//2 - 180))
        render_text(f"Final Score: {score}", small_font, (255, 255, 255), (0,0,0), (WIDTH//2 - 180, HEIGHT//2 - 60))
        render_text(f"High Score: {highscore}", small_font, (255, 215, 0), (0,0,0), (WIDTH//2 - 180, HEIGHT//2 - 10))
        render_text("Press R to Restart", small_font, (0, 255, 0), (0,0,0), (WIDTH//2 - 200, HEIGHT//2 + 60))
        render_text("Press Q to Quit", small_font, (255, 255, 0), (0,0,0), (WIDTH//2 - 200, HEIGHT//2 + 120))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Game loop
def game_loop():
    global highscore
    player = Player()
    zombies = []
    bullets = []
    score = 0
    running = True

    start_time = time.time()
    spawn_rate = 40
    min_spawn_rate = 10

    font = pygame.font.SysFont("arialblack", 36, bold=True)

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        elapsed_time = int(time.time() - start_time)
        spawn_rate = max(min_spawn_rate, 40 - elapsed_time // 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player.alive:
                    bullets.append(Bullet(player.x + 80, player.y + 40))

        screen.blit(background, (0, 0))

        # Displaying current score on top
        render_text(f"Score: {score}", font, (255, 255, 255), (0, 0, 0), (WIDTH//2 - 60, 20))

        player.update(keys)
        player.draw()

        if random.randint(1, spawn_rate) == 1:
            zombies.append(Zombie())

        for bullet in bullets[:]:
            bullet.update()
            bullet.draw()
            if not bullet.alive:
                bullets.remove(bullet)

        for zombie in zombies[:]:
            zombie.update(player)
            zombie.draw()

            if zombie.x < player.x + 50 and zombie.alive:
                player.health -= 1
                zombie.alive = False
                zombies.remove(zombie)

            for bullet in bullets[:]:
                if zombie.alive and bullet.rect().colliderect(zombie.rect()):
                    zombie.health -= 1
                    bullets.remove(bullet)
                    if zombie.health <= 0:
                        zombie.alive = False
                        zombies.remove(zombie)
                        score += 1
                    break

        if player.health <= 0 and player.alive:
            player.alive = False
            game_over_sound.play()
            pygame.time.delay(1000)
            game_over_screen(score)
            return game_loop()

        pygame.display.update()

game_loop()
