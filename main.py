import random
from pgzero.builtins import Actor, keyboard, sounds, music

WIDTH = 800
HEIGHT = 600

#Музыка и звуки
music.set_volume(1)
sound_hit = sounds.hit
sound_hit.set_volume(1.0)
sound_step = sounds.step
sound_step.set_volume(0.3)

# Состояние игры
game_state = 'menu'
sound_on = True
score = 0
level = 1
death_sound_played = False
banana = None  #Только один банан

#  Кнопки интерфейса
sound_button = Actor('sound_on', (750, 50))
home_button = Actor('home_icon', (750, 100))
menu_buttons = {
    'start': Actor('start', (WIDTH // 2 - 50, HEIGHT // 2)),
    'exit': Actor('exit', (WIDTH // 2 + 50, HEIGHT // 2))
}

def update_sound_button():
    sound_button.image = 'sound_on' if sound_on else 'sound_off'

# Герой
class Hero:
    def __init__(self, x, y):
        self.actor = Actor('monkey_right', (x, y))
        self.speed = 2
        self.direction = 'right'
        self.anim_frame = 0
        self.alive = True
        self.step_timer = 0
        self.moving = False
        self.images = {
            'down': ['monkey_right', 'monkey_run_2'],
            'up': ['monkey_jump', 'monkey_jump2'],
            'left': ['monkey_push_1', 'monkey_push2'],
            'right': ['monkey_right', 'monkey_run_1']
        }
        self.update_hitbox()

    def move(self, keys):
        self.moving = False
        if keys.left:
            self.actor.x -= self.speed
            self.direction = 'left'
            self.moving = True
        elif keys.right:
            self.actor.x += self.speed
            self.direction = 'right'
            self.moving = True
        elif keys.up:
            self.actor.y -= self.speed
            self.direction = 'up'
            self.moving = True
        elif keys.down:
            self.actor.y += self.speed
            self.direction = 'down'
            self.moving = True

        self.actor.x = max(self.actor.width // 2, self.actor.x)
        self.actor.y = max(self.actor.height // 2, min(self.actor.y, HEIGHT - self.actor.height // 2))

        if self.moving and sound_on:
            self.step_timer += 1
            if self.step_timer >= 10:
                sound_step.play()
                self.step_timer = 0
        else:
            self.step_timer = 0
            sound_step.stop()

    def update_animation(self):
        if self.moving:
            self.anim_frame = (self.anim_frame + 1) % len(self.images[self.direction])
        else:
            self.anim_frame = 0
        self.actor.image = self.images[self.direction][self.anim_frame]

    def update_hitbox(self):
        self.actor.hitbox = self.actor._rect.inflate(-10, -30)

    def draw(self):
        self.actor.draw()

    def draw_dead(self):
        dead_actor = Actor('monkey_dead', (self.actor.x, self.actor.y))
        dead_actor.draw()

# Враг
class Enemy:
    def __init__(self, x, y, patrol_area):
        self.actor = Actor('croc', (x, y))
        self.speed = 1 + level * 0.2
        self.direction = 'left'
        self.patrol_area = patrol_area
        self.anim_frame = 0
        self.images = {
            'right': ['croc_walk', 'croc_walk'],
            'left': ['croc', 'croc']
        }
        self.update_hitbox()

    def patrol(self):
        if self.direction == 'left':
            self.actor.x -= self.speed
            if self.actor.x < max(self.patrol_area[0], self.actor.width // 2):
                self.actor.x = max(self.patrol_area[0], self.actor.width // 2)
                self.direction = 'right'
        else:
            self.actor.x += self.speed
            if self.actor.x > min(self.patrol_area[1], WIDTH - self.actor.width // 2):
                self.actor.x = min(self.patrol_area[1], WIDTH - self.actor.width // 2)
                self.direction = 'left'

    def update_animation(self):
        self.anim_frame = (self.anim_frame + 1) % len(self.images[self.direction])
        self.actor.image = self.images[self.direction][self.anim_frame]

    def update_hitbox(self):
        self.actor.hitbox = self.actor._rect.inflate(-70, -50)

    def draw(self):
        self.actor.draw()

# Банан
class Banana:
    def __init__(self, x, y):
        self.actor = Actor('banana', (x, y))
        self.speed = 5
        self.active = True
        self.update_hitbox()

    def move(self):
        self.actor.x += self.speed
        if self.actor.x > WIDTH:
            self.active = False
        self.update_hitbox()

    def draw(self):
        if self.active:
            self.actor.draw()

    def update_hitbox(self):
        self.actor.hitbox = self.actor._rect.inflate(-10, -10)

# Игровые объекты
hero = Hero(50, HEIGHT // 2)
enemies = []

def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(level):
        while True:
            x = random.randint(WIDTH - WIDTH // 3, WIDTH - 50)
            y = random.randint(100, HEIGHT - 100)
            dx = abs(x - hero.actor.x)
            dy = abs(y - hero.actor.y)
            if dx > 150 and dy > 100:
                enemies.append(Enemy(x, y, (WIDTH // 2, WIDTH - 50)))
                break

def start_game():
    global game_state, score, level, hero, death_sound_played, banana
    game_state = 'game'
    score = 0
    level = 1
    hero = Hero(50, HEIGHT // 2)
    hero.alive = True
    death_sound_played = False
    banana = None
    spawn_enemies()
    update_sound_button()
    if sound_on:
        music.stop()
        music.play('music')

def check_collisions():
    for enemy in enemies:
        if hero.actor.hitbox.colliderect(enemy.actor.hitbox):
            hero.alive = False
            if sound_on:
                sound_step.stop()
                music.stop()
            clock.schedule_unique(switch_to_menu, 1.0)
            break

def switch_to_menu():
    global game_state
    game_state = 'menu'

def next_level():
    global level, score
    level += 1
    score += 100
    hero.actor.pos = (50, HEIGHT // 2)
    spawn_enemies()

def draw():
    global death_sound_played
    screen.clear()
    if game_state == 'menu':
        screen.blit('home', (0, 0))
        for btn in menu_buttons.values():
            btn.draw()
        sound_button.draw()
        if not hero.alive:
            hero.draw_dead()
            screen.draw.text("Вы погибли!", center=(WIDTH // 2, 50), fontsize=50, color="red")
            if sound_on and not death_sound_played:
                sound_hit.play()
                death_sound_played = True
    elif game_state == 'game':
        screen.blit('stone_base_color', (0, 0))
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        if banana:
            banana.draw()
        sound_button.draw()
        home_button.draw()
        screen.draw.text(f"Очки: {score}", topleft=(10, 10), fontsize=30, color="white")
        screen.draw.text(f"Уровень: {level}", topleft=(10, 40), fontsize=30, color="white")

def update():
    global score, banana

    if game_state == 'game' and hero.alive:
        hero.move(keyboard)
        hero.update_animation()
        hero.update_hitbox()

        # Бросок банана
        if keyboard.space and banana is None:
            banana = Banana(hero.actor.x + 20, hero.actor.y)

        # Обновление банана
        if banana:
            banana.move()
            for enemy in enemies:
                if banana.active and enemy.actor.hitbox.colliderect(banana.actor.hitbox):
                    enemies.remove(enemy)
                    banana.active = False
                    banana = None
                    score += 50
                    break
            if banana and not banana.active:
                banana = None

        # Обновление врагов
        for enemy in enemies:
            enemy.patrol()
            enemy.update_animation()
            enemy.update_hitbox()

        check_collisions()

        if hero.actor.x > WIDTH - 50:
            next_level()


def on_mouse_down(pos):
    global game_state, sound_on, hero, score, level, death_sound_played, banana

    # Переключение звука
    if sound_button.collidepoint(pos):
        sound_on = not sound_on
        update_sound_button()
        if sound_on:
            music.play('music')
        else:
            music.stop()

    # Обработка кликов в меню
    if game_state == 'menu':
        if menu_buttons['start'].collidepoint(pos):
            start_game()
        elif menu_buttons['exit'].collidepoint(pos):
            exit()

    # Обработка клика по кнопке "домой" в игре
    elif game_state == 'game':
        if home_button.collidepoint(pos):
            game_state = 'menu'
            hero.alive = True
            death_sound_played = False
            banana = None
            update_sound_button()

     






