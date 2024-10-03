import pygame
import math
import random
import time
import sys
import os
import configparser

base_path = os.path.dirname(os.path.abspath(__file__))

def load_settings():
    config = configparser.ConfigParser()
    config_file = os.path.join(base_path, 'settings.cfg')
    
    # Настройки по умолчанию
    default_settings = {
        'resolution': '800x600',
        'fullscreen': 'False',
        'volume_music': '1.0',
        'volume_hits': '1.0',
        'volume_other': '1.0'
    }
    
    if os.path.exists(config_file):
        config.read(config_file)
        settings = {
            'resolution': tuple(map(int, config.get('Settings', 'resolution').split('x'))),
            'fullscreen': config.getboolean('Settings', 'fullscreen'),
            'volume_music': config.getfloat('Settings', 'volume_music'),
            'volume_hits': config.getfloat('Settings', 'volume_hits'),
            'volume_other': config.getfloat('Settings', 'volume_other')
        }
    else:
        # Используем настройки по умолчанию и сохраняем их
        settings = {
            'resolution': tuple(map(int, default_settings['resolution'].split('x'))),
            'fullscreen': default_settings['fullscreen'] == 'True',
            'volume_music': float(default_settings['volume_music']),
            'volume_hits': float(default_settings['volume_hits']),
            'volume_other': float(default_settings['volume_other'])
        }
        save_settings(settings)
    
    return settings

def save_settings(settings):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'resolution': f"{settings['resolution'][0]}x{settings['resolution'][1]}",
        'fullscreen': str(settings['fullscreen']),
        'volume_music': str(settings['volume_music']),
        'volume_hits': str(settings['volume_hits']),
        'volume_other': str(settings['volume_other'])
    }
    
    config_file = os.path.join(base_path, 'settings.cfg')
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Настройки
settings = load_settings()

# Игровые константы
SCREEN_WIDTH, SCREEN_HEIGHT = settings['resolution']
FONT_SIZE = 24
PLAYER_SYMBOL = '@'
ENEMY_SYMBOL = 'M'
SHOOTER_SYMBOL = 'S'
HEALTH_SYMBOL = '+'
PROJECTILE_SYMBOL = '*'
BACKGROUND_COLOR = (0, 0, 0)  # Черный
TEXT_COLOR = (255, 255, 255)  # Белый
PLAYER_COLOR = (0, 255, 0)  # Зеленый
ENEMY_COLOR = (255, 0, 0)  # Красный
HEALTH_COLOR = (0, 255, 0)  # Зеленый для аптечек
PROJECTILE_COLOR = (255, 255, 0)  # Желтый для снарядов
ENEMY_DEFAULT_COLOR = (255, 255, 255)  # Белый для обычных врагов
INITIAL_ENEMY_COUNT = 3
WAVE_INTERVAL = 3  # Время между волнами в секундах
MOUSE_FOLLOW_SPEED = 0.1  # Инерция для следования игрока за мышью
KNOCKBACK_STRENGTH = 10  # Сила отбрасывания при попадании по врагу
PLAYER_DAMAGE = 1  # Урон, наносимый игроком за удар
DAMAGE_COOLDOWN = 400  # Кулдаун в миллисекундах для атак
SHAKE_INTENSITY = 2  # Интенсивность тряски врага перед тем, как он станет красным
INVULNERABILITY_DURATION = 1000  # Продолжительность неуязвимости игрока в начале волны (в мс)

# Инициализация Pygame и микшера для звука
pygame.init()
pygame.mixer.init()

# Глобальные переменные для экрана и шрифта
screen = None
font = None

def apply_display_settings():
    global screen, font, SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH, SCREEN_HEIGHT = settings['resolution']
    
    if settings['fullscreen']:
        # Получаем текущее разрешение дисплея пользователя
        infoObject = pygame.display.Info()
        display_resolution = (infoObject.current_w, infoObject.current_h)
        screen = pygame.display.set_mode(display_resolution, pygame.FULLSCREEN, pygame.NOFRAME)
        SCREEN_WIDTH, SCREEN_HEIGHT = display_resolution  # Обновляем глобальные переменные
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    
    # Обновляем шрифт, если необходимо
    font = pygame.font.SysFont('Courier', FONT_SIZE)
    
    # Сохраняем настройки
    save_settings(settings)
    
icon = pygame.Surface((32, 32), pygame.SRCALPHA)  # Создаем прозрачную поверхность
pygame.display.set_icon(icon)

def apply_volume_settings():
    pygame.mixer.music.set_volume(settings['volume_music'])

    # Настройка громкости звуков ударов
    for sound in hit_sounds:
        sound.set_volume(settings['volume_hits'])

    # Настройка громкости остальных звуков
    other_sounds = [
        damage_sound, level_up_sound, exp_gain_sound, health_pickup_sound, upgrade_select_sound,
        shooter_fire_sound, countdown_sound, game_over_sound
    ]
    for sound in other_sounds:
        sound.set_volume(settings['volume_other'])
    
    # Сохраняем настройки
    save_settings(settings)

# Загрузка звуков из папки audio
hit_sounds = [
    pygame.mixer.Sound(os.path.join(base_path, 'audio', 'hit1.wav')),
    pygame.mixer.Sound(os.path.join(base_path, 'audio', 'hit2.wav')),
    pygame.mixer.Sound(os.path.join(base_path, 'audio', 'hit3.wav'))
]
damage_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'damage.wav'))
level_up_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'level_up.wav'))
exp_gain_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'exp_gain.wav'))
health_pickup_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'health_pickup.wav'))
upgrade_select_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'upgrade_select.wav'))
shooter_fire_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'shooter_fire.wav'))
countdown_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'countdown.wav'))
game_over_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'game_over.wav'))
pygame.mixer.music.load(os.path.join(base_path, 'audio', 'background_music.wav'))

# Применение начальных настроек
apply_display_settings()
apply_volume_settings()

# Воспроизведение фоновой музыки
pygame.mixer.music.play(-1, 0.0)  # Цикл бесконечно

# Установка заголовка окна
pygame.display.set_caption('<The Game>')

# Настройка шрифтов
font = pygame.font.SysFont('Courier', FONT_SIZE)

# Инициализация часов
clock = pygame.time.Clock()

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.exp = 0
        self.exp_to_level_up = 10
        self.hp = 10
        self.max_hp = 10
        self.speed = 1
        self.damage = PLAYER_DAMAGE
        self.defense = 0
        self.last_hit_time = pygame.time.get_ticks()  # Время последнего удара

    def move(self, target_x, target_y):
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.x += MOUSE_FOLLOW_SPEED * direction_x
            self.y += MOUSE_FOLLOW_SPEED * direction_y

    def gain_exp(self, amount):
        self.exp += round(amount, 1)  # Округление опыта до одного десятичного
        pygame.mixer.Sound.play(exp_gain_sound)  # Воспроизведение звука получения опыта
        while self.exp >= self.exp_to_level_up:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level_up
        self.exp_to_level_up += 10  # Увеличение требования к опыту с каждым уровнем
        pygame.mixer.Sound.play(level_up_sound)  # Воспроизведение звука повышения уровня
        upgrade_menu(self)  # Вызов меню улучшений при повышении уровня

    def apply_damage(self, damage):
        # Защита снижает урон, но урон не может быть меньше 1
        actual_damage = max(1, damage * (1 - self.defense / 100))
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            pygame.mixer.Sound.play(damage_sound)  # Воспроизведение звука урона
            return True  # Сигнализирует о смерти игрока
        pygame.mixer.Sound.play(damage_sound)  # Воспроизведение звука урона, если еще жив
        return False

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

# Класс аптечки здоровья
class HealthPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        draw_text(HEALTH_SYMBOL, font, HEALTH_COLOR, self.x, self.y)

    def is_colliding(self, player):
        return math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2) < FONT_SIZE

# Класс снаряда
class Projectile:
    def __init__(self, x, y, dx, dy, damage, follow_player=False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage  # Урон снаряда
        self.lifetime = 2000  # Снаряды существуют 2 секунды
        self.speed = 3  # Начальная скорость снаряда
        self.start_time = pygame.time.get_ticks()
        self.follow_player = follow_player  # Следовать за игроком

    def update(self, player_x=None, player_y=None):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.lifetime:
            return False  # Снаряд исчезает
        self.speed = max(self.speed - 0.05, 0)  # Постепенное замедление снаряда

        if self.follow_player and player_x is not None and player_y is not None:
            # Если снаряд должен следовать за игроком
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > 0:
                self.dx = dx / distance
                self.dy = dy / distance

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        return True

    def draw(self, surface):
        draw_text(PROJECTILE_SYMBOL, font, PROJECTILE_COLOR, int(self.x), int(self.y))

    def is_colliding(self, player):
        return math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2) < FONT_SIZE

# Класс врага (включая стрелков)
class Enemy:
    def __init__(self, x, y, is_shooter=False, wave=1):
        self.x = x
        self.y = y
        base_hp = 3
        base_damage = 1
        self.hp = base_hp * (1 + 0.05 * (wave - 1))  # Враги становятся сильнее с каждой волной
        self.damage = base_damage * (1 + 0.05 * (wave - 1))  # Урон врагов увеличивается с волнами
        self.color = ENEMY_DEFAULT_COLOR
        self.damage_timer = random.randint(1000, 3000) + random.randint(0, 5000)  # Случайный таймер
        self.red_duration = 2000  # Как долго враг остается красным
        self.last_hit_time = pygame.time.get_ticks()
        self.is_dead = False
        self.shaking = False
        self.shake_start_time = 0
        self.is_shooter = is_shooter  # Является ли враг стрелком?
        self.shoot_cooldown = 2000 if is_shooter else None  # Кулдаун между выстрелами для стрелков
        self.last_shot_time = pygame.time.get_ticks() if is_shooter else None
        self.preferred_distance = random.randint(150, 250)  # Предпочтительное расстояние до игрока

    def move_towards_player(self, player_x, player_y, enemies):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            if self.is_shooter:
                # Стрелки поддерживают расстояние от игрока
                if distance > self.preferred_distance:
                    move_x = (dx / distance)
                    move_y = (dy / distance)
                elif distance < self.preferred_distance - 20:
                    move_x = -(dx / distance)
                    move_y = -(dy / distance)
                else:
                    move_x = 0
                    move_y = 0
            else:
                # Обычные враги движутся к игроку
                move_x = (dx / distance)
                move_y = (dy / distance)
        else:
            move_x = 0
            move_y = 0

        # Корректировка движения для избегания наложения с другими врагами
        move_x, move_y = self.avoid_collisions(move_x, move_y, enemies)

        # Перемещение врага
        self.x += move_x
        self.y += move_y

    def avoid_collisions(self, move_x, move_y, enemies):
        for other in enemies:
            if other != self:
                dist_to_other = math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)
                if dist_to_other < FONT_SIZE:
                    # Враги слишком близко, корректируем движение
                    repel_x = self.x - other.x
                    repel_y = self.y - other.y
                    repel_distance = math.sqrt(repel_x ** 2 + repel_y ** 2)
                    if repel_distance > 0:
                        repel_x /= repel_distance
                        repel_y /= repel_distance
                        # Корректируем движение
                        move_x += repel_x
                        move_y += repel_y
        # Нормализуем вектор движения
        total_movement = math.sqrt(move_x ** 2 + move_y ** 2)
        if total_movement > 0:
            move_x = (move_x / total_movement)
            move_y = (move_y / total_movement)
        else:
            move_x, move_y = 0, 0
        return move_x, move_y

    def is_colliding(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2) < FONT_SIZE

    def knockback(self, player_x, player_y):
        dx = self.x - player_x
        dy = self.y - player_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            # Вычисление отбрасывания
            self.x += KNOCKBACK_STRENGTH * (dx / distance)
            self.y += KNOCKBACK_STRENGTH * (dy / distance)

        # Обеспечиваем, чтобы враг оставался внутри экрана
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - FONT_SIZE:
            self.x = SCREEN_WIDTH - FONT_SIZE

        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - FONT_SIZE:
            self.y = SCREEN_HEIGHT - FONT_SIZE

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_dead = True  # Помечаем врага как мертвого

    def shoot(self, player_x, player_y):
        if not self.is_shooter:
            return None  # Только стрелки стреляют

        current_time = pygame.time.get_ticks()

        # Проверяем, прошло ли достаточно времени с последнего выстрела
        if current_time - self.last_shot_time > self.shoot_cooldown:
            if not self.shaking:
                # Начинаем тряску перед выстрелом
                self.shaking = True
                self.shake_start_time = current_time
            else:
                # Если тряска завершена, стреляем
                if current_time - self.shake_start_time >= 500:  # Тряска длится 500 мс
                    self.shaking = False  # Прекращаем тряску
                    self.last_shot_time = current_time  # Обновляем время последнего выстрела

                    # Вычисляем направление выстрела
                    dx = player_x - self.x
                    dy = player_y - self.y
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance > 0:
                        pygame.mixer.Sound.play(shooter_fire_sound)  # Воспроизведение звука выстрела
                        return Projectile(self.x, self.y, dx / distance, dy / distance, self.damage, follow_player=True)

        return None

    def update(self, delta_time):
        self.damage_timer -= delta_time

        # Логика тряски для стрелков
        if self.is_shooter and self.shaking:
            elapsed = pygame.time.get_ticks() - self.shake_start_time
            if elapsed < 500:  # Тряска продолжается 500 мс
                self.x += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                self.y += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            # Не сбрасываем self.shaking здесь; метод shoot() обрабатывает это

        if self.damage_timer <= 0 and not self.shaking:
            self.shaking = True
            self.shake_start_time = pygame.time.get_ticks()
            self.color = ENEMY_DEFAULT_COLOR
            self.red_duration = 2000

        if self.shaking and not self.is_shooter:
            elapsed = pygame.time.get_ticks() - self.shake_start_time
            if elapsed < 1000:
                self.x += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                self.y += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            elif elapsed >= 1000 and self.color != ENEMY_COLOR:
                self.color = ENEMY_COLOR
            elif elapsed >= 2000:
                self.shaking = False
                self.color = ENEMY_DEFAULT_COLOR
                self.damage_timer = random.randint(1000, 3000) + random.randint(0, 5000)

# Класс для отображения чисел урона
class DamageNumber:
    def __init__(self, x, y, damage, color, lifetime=1000):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = lifetime  # Как долго число урона остается на экране
        self.start_time = pygame.time.get_ticks()

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        self.y -= 0.05  # Медленное поднятие числа урона
        if elapsed_time > self.lifetime:
            return False  # Сигнализирует о необходимости удаления числа урона
        return True

    def draw(self, surface):
        draw_text(str(self.damage), font, self.color, int(self.x), int(self.y))

def spawn_health_pickup(enemy_x, enemy_y):
    if random.random() < 0.15:  # 15% шанс появления аптечки
        return HealthPickup(enemy_x, enemy_y)
    return None

# Функция для создания врагов и аптечек
def spawn_enemies(count, wave):
    enemies = []
    for _ in range(count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        is_shooter = random.random() < 0.3  # 30% шанс быть стрелком
        enemies.append(Enemy(x, y, is_shooter, wave))
    return enemies

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def handle_collisions(player, enemies, damage_numbers, wave, wave_start_time, projectiles, health_pickups):
    current_time = pygame.time.get_ticks()

    # Задержка урона в течение первой секунды волны
    if current_time - wave_start_time < INVULNERABILITY_DURATION:
        return False

    game_over = False

    for enemy in enemies:
        # Проверка столкновения между игроком и врагом
        if math.sqrt((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) < FONT_SIZE:
            # Если враг красный, наносим урон
            if enemy.color == ENEMY_COLOR and current_time - enemy.last_hit_time > DAMAGE_COOLDOWN:
                enemy.last_hit_time = current_time
                damage = enemy.damage
                player_died = player.apply_damage(damage)
                damage_numbers.append(DamageNumber(player.x, player.y + 30, round(damage, 1), (255, 0, 0)))
                if player_died:
                    return True  # Сигнализирует о завершении игры

            # Игрок наносит урон врагу с кулдауном
            if current_time - player.last_hit_time > DAMAGE_COOLDOWN:
                player.last_hit_time = current_time
                pygame.mixer.Sound.play(random.choice(hit_sounds))
                enemy.take_damage(player.damage)
                enemy.knockback(player.x, player.y)
                damage_numbers.append(DamageNumber(enemy.x, enemy.y - 20, player.damage, TEXT_COLOR))

                # Получение опыта за убийство врага
                if enemy.is_dead:
                    if enemy.is_shooter:
                        exp_gain = round(1.2 + 0.1 * wave, 1)  # Стрелки дают больше опыта
                    else:
                        exp_gain = round(0.9 + 0.1 * wave, 1)
                    player.gain_exp(exp_gain)
                    damage_numbers.append(DamageNumber(player.x, player.y + 30, f"+{exp_gain} EXP", (0, 255, 0)))

                    # 15% шанс появления аптечки
                    health_pickup = spawn_health_pickup(enemy.x, enemy.y)
                    if health_pickup:
                        health_pickups.append(health_pickup)

    # Обработка столкновений с снарядами
    for projectile in projectiles[:]:
        if projectile.is_colliding(player):
            projectiles.remove(projectile)
            damage = projectile.damage
            player_died = player.apply_damage(damage)
            damage_numbers.append(DamageNumber(player.x, player.y + 30, round(damage, 1), (255, 0, 0)))
            if player_died:
                return True

    return game_over

def upgrade_menu(player):
    selected = None
    upgrade_font = pygame.font.SysFont('Courier', 36)
    while selected is None:
        screen.fill(BACKGROUND_COLOR)
        # Отображение заголовка меню улучшений
        title_text = upgrade_font.render("Upgrade Menu", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        # Опции улучшений
        options = ['1. Increase HP', '2. Increase Damage', '3. Increase Defense']
        for i, option in enumerate(options):
            option_text = font.render(option, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50 + i * 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.max_hp += 1
                    player.hp += 1
                    selected = "hp"
                    pygame.mixer.Sound.play(upgrade_select_sound)
                elif event.key == pygame.K_2:
                    player.damage += 1
                    selected = "damage"
                    pygame.mixer.Sound.play(upgrade_select_sound)
                elif event.key == pygame.K_3:
                    if player.defense < 90:
                        player.defense += 1
                    selected = "defense"
                    pygame.mixer.Sound.play(upgrade_select_sound)

        clock.tick(60)

def wave_countdown():
    countdown_start_time = pygame.time.get_ticks()
    countdown_duration = 3000  # 3 секунды
    last_second = None
    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - countdown_start_time
        remaining_time = countdown_duration - elapsed_time
        if remaining_time <= 0:
            break
        seconds_left = int(remaining_time / 1000) + 1
        if seconds_left != last_second:
            last_second = seconds_left
            pygame.mixer.Sound.play(countdown_sound)
        screen.fill(BACKGROUND_COLOR)
        countdown_text = font.render(f'Next wave in {seconds_left}...', True, TEXT_COLOR)
        screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        # Обработка событий для предотвращения зависания
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)       

def save_settings(settings):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'resolution': f"{settings['resolution'][0]}x{settings['resolution'][1]}",
        'fullscreen': str(settings['fullscreen']),
        'volume_music': str(settings['volume_music']),
        'volume_hits': str(settings['volume_hits']),
        'volume_other': str(settings['volume_other'])
    }
    
    config_file = os.path.join(base_path, 'settings.cfg')
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def main_menu():
    menu_running = True
    selected_option = 0  # 0: Начать игру, 1: Настройки, 2: Выход

    menu_font = pygame.font.SysFont('Courier', 48)

    options = ['Start Game', 'Settings', 'Exit']

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        # Начать игру
                        menu_running = False
                    elif selected_option == 1:
                        # Открыть настройки
                        settings_menu()
                    elif selected_option == 2:
                        # Выход
                        pygame.quit()
                        sys.exit()

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение названия игры
        title_text = menu_font.render('<The Game>', True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Отображение опций меню
        for i, option in enumerate(options):
            if i == selected_option:
                option_display = '> ' + option
            else:
                option_display = option
            option_text = font.render(option_display, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 250 + i * 50))

        pygame.display.flip()
        clock.tick(60)

def settings_menu():
    settings_running = True
    selected_option = 0
    options = ['Resolution', 'Fullscreen Mode', 'Music Volume', 'Hit Volume', 'Other Sounds Volume', 'Back']

    while settings_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_option] == 'Resolution':
                        change_resolution()
                    elif options[selected_option] == 'Fullscreen Mode':
                        settings['fullscreen'] = not settings['fullscreen']
                        apply_display_settings()
                    elif options[selected_option] == 'Music Volume':
                        adjust_volume('volume_music')
                    elif options[selected_option] == 'Hit Volume':
                        adjust_volume('volume_hits')
                    elif options[selected_option] == 'Other Sounds Volume':
                        adjust_volume('volume_other')
                    elif options[selected_option] == 'Back':
                        settings_running = False

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение заголовка меню настроек
        settings_title = pygame.font.SysFont('Courier', 48).render('Settings', True, TEXT_COLOR)
        screen.blit(settings_title, (SCREEN_WIDTH // 2 - settings_title.get_width() // 2, 50))

        # Отображение опций настроек с текущими значениями
        for i, option in enumerate(options):
            if option == 'Fullscreen Mode':
                status = 'ON' if settings['fullscreen'] else 'OFF'
                option_display = f"{option}: {status}"
            elif option == 'Resolution':
                option_display = f"{option}: {settings['resolution'][0]}x{settings['resolution'][1]}"
            elif option == 'Music Volume':
                volume_value = int(settings['volume_music'] * 100)
                option_display = f"{option}: {volume_value}%"
            elif option == 'Hit Volume':
                volume_value = int(settings['volume_hits'] * 100)
                option_display = f"{option}: {volume_value}%"
            elif option == 'Other Sounds Volume':
                volume_value = int(settings['volume_other'] * 100)
                option_display = f"{option}: {volume_value}%"
            else:
                option_display = option

            if i == selected_option:
                option_display = '> ' + option_display
            option_text = font.render(option_display, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 150 + i * 40))

        pygame.display.flip()
        clock.tick(60)

def change_resolution():
    # Получаем текущее разрешение экрана пользователя
    infoObject = pygame.display.Info()
    current_display_resolution = (infoObject.current_w, infoObject.current_h)
    
    # Добавляем текущие разрешения и стандартные варианты
    resolutions = [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1366, 768),
        (1600, 900),
        (1920, 1080),
        (2560, 1440),
        current_display_resolution  # Добавляем текущее разрешение дисплея
    ]
    
    # Убедимся, что текущее разрешение не добавлено несколько раз
    if current_display_resolution not in resolutions:
        resolutions.append(current_display_resolution)
    
    # Определяем индекс текущего разрешения
    try:
        res_selected = resolutions.index(settings['resolution'])
    except ValueError:
        res_selected = 0
    
    changing_resolution = True

    while changing_resolution:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    res_selected = (res_selected - 1) % len(resolutions)
                elif event.key == pygame.K_RIGHT:
                    res_selected = (res_selected + 1) % len(resolutions)
                elif event.key == pygame.K_RETURN:
                    settings['resolution'] = resolutions[res_selected]
                    apply_display_settings()
                    changing_resolution = False
                elif event.key == pygame.K_ESCAPE:
                    changing_resolution = False

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение текущего разрешения
        resolution_text = font.render(f"Resolution: {resolutions[res_selected][0]}x{resolutions[res_selected][1]}", True, TEXT_COLOR)
        screen.blit(resolution_text, (SCREEN_WIDTH // 2 - resolution_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

def adjust_volume(volume_key):
    adjusting = True
    while adjusting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    settings[volume_key] = max(0.0, settings[volume_key] - 0.1)
                    apply_volume_settings()
                elif event.key == pygame.K_RIGHT:
                    settings[volume_key] = min(1.0, settings[volume_key] + 0.1)
                    apply_volume_settings()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    adjusting = False

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение текущего уровня громкости
        volume_value = int(settings[volume_key] * 100)
        volume_text = font.render(f"{volume_key.replace('_', ' ').title()}: {volume_value}%", True, TEXT_COLOR)
        screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

def main():
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies = []
    damage_numbers = []
    health_pickups = []
    projectiles = []
    wave = 1
    wave_start_time = pygame.time.get_ticks()
    paused = False

    running = True

    while running:
        delta_time = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

        if not paused:
            screen.fill(BACKGROUND_COLOR)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player.move(mouse_x, mouse_y)

            # Отображение персонажа игрока
            draw_text(PLAYER_SYMBOL, font, PLAYER_COLOR, int(player.x), int(player.y))

            if not enemies:
                if player.hp > 0:
                    wave_countdown()
                    wave_start_time = pygame.time.get_ticks()  # Отслеживание начала волны
                    enemies = spawn_enemies(wave * INITIAL_ENEMY_COUNT, wave)
                    wave += 1
                else:
                    pygame.mixer.Sound.play(game_over_sound)
                    game_over_text = pygame.font.SysFont('Courier', 48).render("Game Over", True, TEXT_COLOR)
                    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                    pygame.display.flip()
                    time.sleep(2)
                    return  # Возврат в главное меню

            # Обновление и отображение врагов и снарядов
            for enemy in enemies:
                enemy.move_towards_player(player.x, player.y, enemies)
                enemy.update(delta_time)
                if not enemy.is_dead:
                    if enemy.is_shooter:
                        projectile = enemy.shoot(player.x, player.y)
                        if projectile:
                            projectiles.append(projectile)
                    symbol = SHOOTER_SYMBOL if enemy.is_shooter else ENEMY_SYMBOL
                    draw_text(symbol, font, enemy.color, enemy.x, enemy.y)

            for projectile in projectiles[:]:
                if not projectile.update(player.x, player.y):
                    projectiles.remove(projectile)
                else:
                    projectile.draw(screen)

            # Обработка столкновений и проверка на окончание игры
            game_over = handle_collisions(player, enemies, damage_numbers, wave, wave_start_time, projectiles, health_pickups)
            if game_over:
                pygame.mixer.Sound.play(game_over_sound)
                game_over_text = pygame.font.SysFont('Courier', 48).render("Game Over", True, TEXT_COLOR)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                pygame.display.flip()
                time.sleep(2)
                return  # Возврат в главное меню

            # Обновление и отображение чисел урона
            for dmg_num in damage_numbers[:]:
                if not dmg_num.update():
                    damage_numbers.remove(dmg_num)
                else:
                    dmg_num.draw(screen)

            # Обновление и отображение аптечек здоровья
            for health_pickup in health_pickups[:]:
                health_pickup.draw(screen)
                if health_pickup.is_colliding(player):
                    player.heal(1)
                    health_pickups.remove(health_pickup)
                    pygame.mixer.Sound.play(health_pickup_sound)

            # Отображение статистики игрока (уровень, здоровье и опыт)
            stats_text = f'Level: {player.level}  HP: {player.hp:.1f}/{player.max_hp:.1f}  EXP: {player.exp:.1f}/{player.exp_to_level_up}'
            draw_text(stats_text, font, TEXT_COLOR, 10, 10)

            # Удаление мертвых врагов
            enemies = [enemy for enemy in enemies if not enemy.is_dead]

            pygame.display.flip()
        else:
            # Отображение состояния паузы
            pause_text = pygame.font.SysFont('Courier', 48).render("Paused", True, TEXT_COLOR)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    while True:
        main_menu()
        main()
