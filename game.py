import pygame
import math
import random
import time
import sys
import os
import configparser
import numpy as np

base_path = os.path.dirname(os.path.abspath(__file__))

def load_settings():
    config = configparser.ConfigParser()
    config_file = os.path.join(base_path, 'settings.cfg')
    
    # Настройки по умолчанию
    default_settings = {
        'resolution': '1280x720',
        'fullscreen': 'False',
        'volume_music': '0.5',
        'volume_hits': '0.5',
        'volume_other': '0.5',
        'language': 'en'
    }
    
    if os.path.exists(config_file):
        config.read(config_file)
        settings = {
            'resolution': tuple(map(int, config.get('Settings', 'resolution').split('x'))),
            'fullscreen': config.getboolean('Settings', 'fullscreen'),
            'volume_music': config.getfloat('Settings', 'volume_music'),
            'volume_hits': config.getfloat('Settings', 'volume_hits'),
            'volume_other': config.getfloat('Settings', 'volume_other'),
            'language': config.get('Settings', 'language', fallback=default_settings['language'])
        }
    else:
        # Используем настройки по умолчанию и сохраняем их
        settings = {
            'resolution': tuple(map(int, default_settings['resolution'].split('x'))),
            'fullscreen': default_settings['fullscreen'] == 'True',
            'volume_music': float(default_settings['volume_music']),
            'volume_hits': float(default_settings['volume_hits']),
            'volume_other': float(default_settings['volume_other']),
            'language': default_settings['language']
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
        'volume_other': str(settings['volume_other']),
        'language': settings['language']
    }
    
    config_file = os.path.join(base_path, 'settings.cfg')
    with open(config_file, 'w') as configfile:
        config.write(configfile)
        
def get_text(key, **kwargs):
    lang = settings.get('language', 'en')
    text = localization.get(lang, {}).get(key, key)  # Возвращаем ключ, если перевод не найден
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Если форматирование не удалось, возвращаем текст без изменений
    return text

# Настройки
settings = load_settings()

# Цвет символа
cursor_color = (218, 136, 245)

# Игровые константы
SCREEN_WIDTH, SCREEN_HEIGHT = settings['resolution']
FONT_SIZE = 28
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
INVULNERABILITY_DURATION = 600  # Продолжительность неуязвимости игрока в начале волны (в мс)

# Локализация
localization = {
    'en': {
        'start_game': 'Start Game',
        'settings': 'Settings',
        'how_to_play': 'How to Play',
        'exit': 'Exit',
        'upgrade_menu': 'Upgrade Menu',
        'increase_hp': 'Increase HP',
        'increase_damage': 'Increase Damage',
        'increase_defense': 'Increase Defense',
        'press_to_select': 'Press 1, 2, or 3 to select an upgrade.',
        'next_wave_in': 'Next wave in',
        'game_over': 'Game Over',
        'paused': 'Paused',
        'hold_to_menu': 'Hold Esc to return to menu.',
        'resolution': 'Resolution',
        'fullscreen_mode': 'Fullscreen Mode',
        'music_volume': 'Music Volume',
        'hit_volume': 'Hit Volume',
        'other_sounds_volume': 'Other Sounds Volume',
        'back': 'Back',
        'how_to_play_title': 'How to Play',
        'how_to_play_instructions': [
            "To begin with, the character '@' will follow your cursor.",
            "All you have to do is touch enemies to deal damage and kill.",
            "However, you should be careful as they may respond.",
            "Collect health pickups '+' to restore HP.",
            "Enemies become stronger with each wave.",
            "To keep up you need to upgrade wisely.",
            "Good luck!",
            "",
            "Press ESC to return to the main menu."
        ],
        'level': 'Level',
        'hp': 'HP',
        'defense': 'DEF',
        'exp': 'EXP',
        'boss': 'Boss',
        'on': 'ON',
        'off': 'OFF',
        'language': 'Language'
    },
    'ru': {
        'start_game': 'Начать игру',
        'settings': 'Настройки',
        'how_to_play': 'Как играть',
        'exit': 'Выход',
        'upgrade_menu': 'Меню улучшений',
        'increase_hp': 'Увеличить HP',
        'increase_damage': 'Увеличить урон',
        'increase_defense': 'Увеличить защиту',
        'press_to_select': 'Нажмите 1, 2 или 3 для выбора улучшения.',
        'next_wave_in': 'Следующая волна через',
        'game_over': 'Игра окончена',
        'paused': 'Пауза',
        'hold_to_menu': 'Удерживайте Esc для возврата в меню.',
        'resolution': 'Разрешение',
        'fullscreen_mode': 'Полноэкранный режим',
        'music_volume': 'Громкость музыки',
        'hit_volume': 'Громкость ударов',
        'other_sounds_volume': 'Громкость остальных звуков',
        'back': 'Назад',
        'how_to_play_title': 'Как играть',
        'how_to_play_instructions': [
            "Персонаж '@' всегда будет следовать за курсором.",
            "Всё, что нужно делать, — касаться врагов, чтобы нанести им урон и убить.",
            "Однако стоит быть осторожным, так как они могут ответить.",
            "Собирай аптечки '+' для восстановления HP.",
            "Враги становятся сильнее с каждой волной.",
            "Чтобы справиться, необходимо разумно улучшаться.",
            "Удачи!",
            "",
            "Нажмите ESC для возврата в главное меню."
        ],
        'level': 'Уровень',
        'hp': 'ОЗ',
        'defense': 'ЗАЩ',
        'exp': 'ОПЫТ',
        'boss': 'Босс',
        'on': 'ВКЛ',
        'off': 'ВЫКЛ',
        'language': 'Язык'
    }
}

# Инициализация Pygame и микшера для звука
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)

# Глобальные переменные для экрана и шрифта
screen = None
font = None

pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)

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
    
# Функция для создания цветовых сдвигов (chromatic aberration)
def chromatic_aberration(surface):
    if random.randint(1, 15) == 5:
        # Получаем массивы цветовых каналов только один раз
        arr = pygame.surfarray.pixels3d(surface)

        # Создаем копии каждого цветового канала
        r_arr = arr[:,:,0].copy()
        g_arr = arr[:,:,1].copy()
        b_arr = arr[:,:,2].copy()

        # Случайные сдвиги для каналов
        shift_x, shift_y = random.randint(-1, 1), random.randint(-1, 1)
        r_arr = np.roll(r_arr, shift_x, axis=0)
        r_arr = np.roll(r_arr, shift_y, axis=1)
        g_arr = np.roll(g_arr, random.randint(-1, 1), axis=0)
        g_arr = np.roll(g_arr, random.randint(-1, 1), axis=1)
        b_arr = np.roll(b_arr, random.randint(-1, 1), axis=0)
        b_arr = np.roll(b_arr, random.randint(-1, 1), axis=1)

        # Собираем снова в одно изображение
        result_surface = pygame.surfarray.make_surface(np.dstack([r_arr, g_arr, b_arr]))
        return result_surface
    else:
        return surface

# Функция для создания горизонтальных полос (scanlines)
scanline_surface_cache = {}

def apply_scanlines(surface, intensity=30, alpha=151):
    # Кэширование поверхности с линиями
    size = surface.get_size()
    if size not in scanline_surface_cache:
        scanline_surface = pygame.Surface(size, pygame.SRCALPHA)
        line_color = (intensity, intensity, intensity, alpha)

        # Рисуем линии через одну строку
        for y in range(0, surface.get_height(), 2):
            pygame.draw.line(scanline_surface, line_color, (0, y), (surface.get_width(), y), 1)
        
        # Кэшируем результат
        scanline_surface_cache[size] = scanline_surface
    else:
        scanline_surface = scanline_surface_cache[size]

    # Накладываем полупрозрачные линии на исходную поверхность
    surface.blit(scanline_surface, (0, 0))

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

shooter_fire_channel = pygame.mixer.Channel(5)
music_channel = pygame.mixer.Channel(6)

# Применение начальных настроек
apply_display_settings()
apply_volume_settings()

# Воспроизведение фоновой музыки
if not pygame.mixer.music.get_busy():
    pygame.mixer.music.play(-1, 0.0)  # Цикл бесконечно

# Загрузка музыки для боя с боссом
boss_music = pygame.mixer.Sound(os.path.join(base_path, 'audio', 'boss_theme.wav'))
boss_music.set_volume(settings['volume_music'])

# Установка заголовка окна
pygame.display.set_caption('Ākēdo')

# Настройка шрифтов
font = pygame.font.SysFont('Courier', FONT_SIZE)
boss_font = pygame.font.SysFont('Courier', FONT_SIZE, bold=True)

# Инициализация часов
clock = pygame.time.Clock()

# Скрываем стандартный курсор
pygame.mouse.set_visible(False)

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
        self.defense = 0.0
        self.last_hit_time = pygame.time.get_ticks()  # Время последнего удара
        self.hp_upgrade_count = 0  # Количество улучшений HP
        self.defense_upgrade_count = 0  # Количество улучшений защиты
        self.health_pickup_heal_amount = 1  # Начальное количество восстанавливаемого HP аптечкой

    def move(self, target_x, target_y):
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.x += MOUSE_FOLLOW_SPEED * direction_x
            self.y += MOUSE_FOLLOW_SPEED * direction_y

        # Ограничение позиции игрока в пределах границ экрана
        self.x = max(0, min(self.x, SCREEN_WIDTH - FONT_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - FONT_SIZE))

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
        current_time = pygame.time.get_ticks()

        # Защита уменьшает урон на 0.2 за каждое улучшение
        damage_reduction = 0.2 * self.defense_upgrade_count
        actual_damage = max(0.1, damage - damage_reduction)  # Урон не может быть меньше 0.1
        self.hp -= actual_damage
        self.last_damage_taken = actual_damage  # Сохраняем фактический урон для отображения
        if self.hp <= 0:
            self.hp = 0
            pygame.mixer.Sound.play(damage_sound)
            return True  # Сигнализирует о смерти игрока
        pygame.mixer.Sound.play(damage_sound)
        return False

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)
        self.hp = round(self.hp, 1)  # Округляем до одного знака после запятой

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
        self.lifetime = 1500  # Снаряды существуют 1.5 секунды
        self.speed = 3  # Начальная скорость снаряда
        self.start_time = pygame.time.get_ticks()
        self.follow_player = follow_player  # Следовать за игроком

    def update(self, player_x=None, player_y=None):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.lifetime:
            return False  # Снаряд исчезает
        self.speed = max(self.speed - 0.019, 0)  # Постепенное замедление снаряда

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
        elapsed_time = pygame.time.get_ticks() - self.start_time
        
        # Время для увеличения и уменьшения
        grow_duration = 300  # Время увеличения снаряда (300 мс)
        shrink_duration = 500  # Время уменьшения снаряда (500 мс)
        final_shrink_start = self.lifetime - shrink_duration

        # Рассчитаем размер снаряда в зависимости от времени
        if elapsed_time < grow_duration:
            scale = 1 + (elapsed_time / grow_duration) * 0.5  # Увеличивается на 50%
        elif elapsed_time > final_shrink_start:
            shrink_factor = (self.lifetime - elapsed_time) / shrink_duration
            scale = 1 + 0.5 * shrink_factor  # Уменьшение в последние 500 мс
        else:
            scale = 1.5  # Стандартный размер после увеличения

        # Создаем шрифт с изменённым размером
        dynamic_font = pygame.font.Font(None, int(FONT_SIZE * scale))

        # Отрисуем снаряд с учетом нового размера
        draw_text(PROJECTILE_SYMBOL, dynamic_font, PROJECTILE_COLOR, int(self.x), int(self.y))

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
                shooter_speed = random.randint(10, 13) / 10
                if distance > self.preferred_distance:
                    move_x = (dx / distance) * shooter_speed
                    move_y = (dy / distance) * shooter_speed
                elif distance < self.preferred_distance - 20:
                    move_x = -(dx / distance)
                    move_y = -(dy / distance)
                else:
                    move_x = 0
                    move_y = 0
            else:
                # Обычные враги движутся к игроку
                enemy_speed = random.randint(10, 15) / 10
                move_x = (dx / distance) * enemy_speed
                move_y = (dy / distance) * enemy_speed
        else:
            move_x = 0
            move_y = 0

        # Корректировка движения для избегания наложения с другими врагами
        move_x, move_y = self.avoid_collisions(move_x, move_y, enemies)

        # Перемещение врага
        self.x += move_x
        self.y += move_y

        # Ограничение позиции врага в пределах границ экрана
        self.x = max(0, min(self.x, SCREEN_WIDTH - FONT_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - FONT_SIZE))

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
                        if not shooter_fire_channel.get_busy():
                            shooter_fire_channel.play(shooter_fire_sound)
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
                
class SuicideEnemy(Enemy):
    def __init__(self, x, y, wave=1):
        super().__init__(x, y, is_shooter=False, wave=wave)
        self.symbol = 'o'
        self.hp = 3 * (1 + 0.05 * (wave - 1))  # Базовое HP увеличивается с волнами
        self.shaking = False
        self.shake_start_time = None
        self.shake_duration = 1500  # Длительность тряски перед взрывом
        self.explode = False  # Флаг для взрыва
        self.wave = wave

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            if not self.shaking:
                self.is_dead = True  # Враг умирает сразу, без взрыва
        else:
            if not self.shaking:
                self.shaking = True
                self.shake_start_time = pygame.time.get_ticks()

    def update(self, delta_time):
        if self.shaking:
            elapsed_time = pygame.time.get_ticks() - self.shake_start_time
            if elapsed_time < self.shake_duration:
                # Тряска врага
                self.x += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                self.y += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            else:
                self.is_dead = True
                self.explode = True  # Враг должен взорваться и выпустить снаряды
        else:
            # Обычное поведение движения к игроку
            pass  # Движение обрабатывается в основном цикле или методом move_towards_player
        
class RusherEnemy(Enemy):
    def __init__(self, x, y, wave=6):
        super().__init__(x, y, is_shooter=False, wave=wave)
        self.symbol = 'R'
        self.rush_speed = 7  # Скорость рывка
        self.rush_inertia = 0.97  # Инерция для замедления рывка
        self.velocity_x = 0  # Начальная скорость по оси X
        self.velocity_y = 0  # Начальная скорость по оси Y
        self.rushing = False
        self.resting = False
        self.rush_start_time = None
        self.rest_start_time = None
        self.shake_duration = 900  # Тряска перед рывком

    def update(self, player_x, player_y, delta_time):
        current_time = pygame.time.get_ticks()

        # Если враг отдыхает после рывка
        if self.resting:
            if current_time - self.rest_start_time >= random.randint(1000, 2500):
                self.resting = False  # Завершение отдыха
                self.color = ENEMY_DEFAULT_COLOR  # Сброс цвета врага на стандартный после отдыха
            return

        # Если враг движется к игроку (рывок)
        if self.rushing:
            # Движение с инерцией
            self.velocity_x *= self.rush_inertia
            self.velocity_y *= self.rush_inertia
            self.x += self.velocity_x
            self.y += self.velocity_y

            if current_time - self.rush_start_time >= 500:  # Рывок длится 500 мс
                self.rushing = False
                self.resting = True
                self.rest_start_time = current_time
                self.color = ENEMY_DEFAULT_COLOR  # Сброс цвета на стандартный после рывка
            return

        # Если враг готовится к рывку (тряска)
        if not self.shaking:
            self.shaking = True
            self.shake_start_time = current_time
        else:
            elapsed_time = current_time - self.shake_start_time
            if elapsed_time >= self.shake_duration:
                self.shaking = False
                self.color = ENEMY_COLOR  # Враг становится красным перед атакой
                self.rushing = True
                self.rush_start_time = current_time

                # Направление к игроку
                dx = player_x - self.x
                dy = player_y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.rush_speed
                    self.velocity_y = (dy / distance) * self.rush_speed
            else:
                self.x += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                self.y += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        
# Класс босса
class Boss(Enemy):
    def __init__(self, x, y, appearance_number=1):
        super().__init__(x, y, is_shooter=False, wave=1)
        self.symbol = 'B'
        # Стартовые характеристики
        base_hp = 69
        base_contact_damage = 3
        base_projectile_damage = 1
        multiplier = 2 ** (appearance_number - 1)  # Увеличение на 2x с каждым появлением

        self.hp = base_hp * multiplier
        self.max_hp = self.hp  # Для отображения полоски здоровья
        self.damage = base_contact_damage * multiplier
        self.projectile_damage = base_projectile_damage * multiplier
        self.color = ENEMY_DEFAULT_COLOR

        # Состояния атаки босса
        self.attack_patterns = ['explode_shot', 'burst_shot', 'melee_attack']
        self.current_attack_index = 0
        self.attack_cooldown = 1500  # Время между атаками в мс
        self.last_attack_time = pygame.time.get_ticks()
        self.shaking = False
        self.shake_start_time = 0
        self.shake_duration = 900  # Длительность тряски перед атакой
        self.is_red = False  # Флаг для состояния атаки в ближнем бою
        self.red_start_time = 0
        self.attack_in_progress = False
        self.next_attack = None

    def update(self, delta_time, player_x, player_y, projectiles):
        current_time = pygame.time.get_ticks()

        # Босс движется к игроку
        self.move_towards_player(player_x, player_y, [])

        if self.attack_in_progress:
            if self.shaking:
                if current_time - self.shake_start_time < self.shake_duration:
                    # Босс трясётся
                    self.x += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                    self.y += random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
                    # Ограничиваем позицию босса в пределах экрана
                    self.x = max(0, min(self.x, SCREEN_WIDTH - FONT_SIZE))
                    self.y = max(0, min(self.y, SCREEN_HEIGHT - FONT_SIZE))
                else:
                    # Тряска закончилась, выполняем атаку
                    self.shaking = False
                    self.execute_attack(player_x, player_y, projectiles)
                    # Запоминаем время окончания атаки для кулдауна
                    self.last_attack_time = current_time
                    self.attack_in_progress = False
                    # Переходим к следующей атаке
                    self.current_attack_index = (self.current_attack_index + 1) % len(self.attack_patterns)
        else:
            # Проверяем, пора ли начать новую атаку
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.perform_attack()

        # Обработка состояния красного цвета для ближней атаки
        if self.is_red:
            if current_time - self.red_start_time >= 2000:
                self.is_red = False  # Босс перестаёт быть красным

    def perform_attack(self):
        # Начинаем тряску перед атакой
        self.shaking = True
        self.shake_start_time = pygame.time.get_ticks()
        # Сохраняем тип следующей атаки
        self.next_attack = self.attack_patterns[self.current_attack_index]
        self.attack_in_progress = True

    def execute_attack(self, player_x, player_y, projectiles):
        # Выполняем атаку после тряски
        if self.next_attack == 'explode_shot':
            self.explode_shot(projectiles)
        elif self.next_attack == 'burst_shot':
            self.burst_shot(player_x, player_y, projectiles)
        elif self.next_attack == 'melee_attack':
            self.is_red = True  # Босс становится красным для ближней атаки
            self.red_start_time = pygame.time.get_ticks()
        # Сбрасываем тип следующей атаки
        self.next_attack = None

    def explode_shot(self, projectiles):
        # Босс выпускает снаряды во все стороны
        num_projectiles = 12
        angle_between_projectiles = 360 / num_projectiles
        for i in range(num_projectiles):
            angle = math.radians(i * angle_between_projectiles)
            dx = math.cos(angle)
            dy = math.sin(angle)
            projectile = Projectile(self.x, self.y, dx, dy, self.projectile_damage)
            projectiles.append(projectile)

    def burst_shot(self, player_x, player_y, projectiles):
        # Босс стреляет очередью из 5-10 снарядов в игрока
        num_shots = random.randint(5, 10)
        for _ in range(num_shots):
            dx = player_x - self.x + random.uniform(-20, 20)  # Немного разброса
            dy = player_y - self.y + random.uniform(-20, 20)
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > 0:
                projectile = Projectile(self.x, self.y, dx / distance, dy / distance, self.projectile_damage)
                projectiles.append(projectile)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_dead = True

# Класс для отображения чисел урона и других чисел
class DamageNumber:
    def __init__(self, player_x, player_y, damage, color, lifetime=1000):
        # Рандомное положение вокруг игрока на небольшом расстоянии
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(20, 40)  # Расстояние от персонажа
        self.x = player_x + math.cos(angle) * distance
        self.y = player_y + math.sin(angle) * distance

        self.damage = damage
        self.color = color
        self.lifetime = lifetime  # Длительность отображения числа
        self.start_time = pygame.time.get_ticks()

        self.initial_font_size = 10  # Начальный размер шрифта
        self.max_font_size = 20      # Максимальный размер шрифта
        self.font_size = self.initial_font_size

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        life_ratio = elapsed_time / self.lifetime
        if life_ratio > 1:
            return False  # Удаляем число после завершения времени жизни

        # Анимация изменения размера числа
        if life_ratio <= 0.5:
            # Увеличиваем размер в первой половине времени жизни
            self.font_size = self.initial_font_size + (self.max_font_size - self.initial_font_size) * (life_ratio * 2)
        else:
            # Уменьшаем размер во второй половине времени жизни
            self.font_size = self.max_font_size - (self.max_font_size - self.initial_font_size) * ((life_ratio - 0.5) * 2)

        return True

    def draw(self, surface):
        temp_font = pygame.font.SysFont('Courier', int(self.font_size))
        text_surface = temp_font.render(str(self.damage), True, self.color)
        # Центрируем текст по координатам x и y
        rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surface, rect)

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
        enemy_type_chance = random.random()
        if wave >= 6 and enemy_type_chance < 0.13:
            enemies.append(RusherEnemy(x, y, wave))
        elif enemy_type_chance > 0.89:
            enemies.append(SuicideEnemy(x, y, wave))
        else:
            is_shooter = random.random() < 0.31
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
            # Если враг красный или босс в состоянии атаки
            if (enemy.color == ENEMY_COLOR or (isinstance(enemy, Boss) and enemy.is_red)) and current_time - enemy.last_hit_time > DAMAGE_COOLDOWN:
                enemy.last_hit_time = current_time
                damage = enemy.damage
                player_died = player.apply_damage(damage)
                damage_numbers.append(DamageNumber(player.x, player.y, round(player.last_damage_taken, 1), (255, 0, 0)))
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
                    if isinstance(enemy, Boss):
                        exp_gain = round(10 + 5 * wave, 1)  # Босс дает больше опыта
                    elif isinstance(enemy, RusherEnemy):
                        exp_gain = round(1.5 + 0.1 * wave, 1)
                    elif enemy.is_shooter:
                        exp_gain = round(1.2 + 0.1 * wave, 1)
                    else:
                        exp_gain = round(0.9 + 0.1 * wave, 1)
                    player.gain_exp(exp_gain)
                    damage_numbers.append(DamageNumber(player.x, player.y, f"+{exp_gain} {get_text('exp')}", (0, 0, 255)))

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
            damage_numbers.append(DamageNumber(player.x, player.y + 30, round(player.last_damage_taken, 1), (255, 0, 0)))
            if player_died:
                return True

    return game_over

def upgrade_menu(player):
    selected = None
    upgrade_font = pygame.font.SysFont('Courier', 36)
    hint_font = pygame.font.SysFont('Courier', 28)  # Шрифт для подсказки
    while selected is None:
        screen.fill(BACKGROUND_COLOR)
        # Отображение заголовка меню улучшений
        title_text = upgrade_font.render(get_text('upgrade_menu'), True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        # Опции улучшений
        options = [
            f"1. {get_text('increase_hp')}",
            f"2. {get_text('increase_damage')}",
            f"3. {get_text('increase_defense')}"
        ]
        for i, option in enumerate(options):
            option_text = font.render(option, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50 + i * 40))
        # Подсказка
        hint_text = hint_font.render(get_text('press_to_select'), True, TEXT_COLOR)
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 100))
        
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Увеличиваем максимальное HP на 10%
                    player.max_hp *= 1.10
                    player.max_hp = round(player.max_hp, 1)  # Округляем до одного знака после запятой
                    player.hp = player.max_hp  # Восстанавливаем HP до максимума
                    player.hp_upgrade_count += 1  # Увеличиваем счетчик улучшений HP

                    # Увеличиваем количество восстанавливаемого HP аптечкой на 20%
                    player.health_pickup_heal_amount *= 1.20
                    player.health_pickup_heal_amount = round(player.health_pickup_heal_amount, 1)  # Округляем

                    selected = "hp"
                    pygame.mixer.Sound.play(upgrade_select_sound)
                elif event.key == pygame.K_2:
                    player.damage += 1
                    selected = "damage"
                    pygame.mixer.Sound.play(upgrade_select_sound)
                elif event.key == pygame.K_3:
                    player.defense_upgrade_count += 1
                    player.defense = 0.2 * player.defense_upgrade_count  # Обновляем значение защиты
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
        countdown_text = font.render(f'{get_text('next_wave_in')} {seconds_left}...', True, TEXT_COLOR)
        screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2))
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))
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
        'volume_other': str(settings['volume_other']),
        'language': settings['language']
    }
    
    config_file = os.path.join(base_path, 'settings.cfg')
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def main_menu():
    menu_running = True
    selected_option = 0  # 0: Начать игру, 1: Настройки, 2: How to play, 3: Выход

    menu_font = pygame.font.SysFont('Courier', 56)

    options = [
        get_text('start_game'),
        get_text('settings'),
        get_text('how_to_play'),
        get_text('exit')
    ]

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
                        # Start Game
                        menu_running = False
                    elif selected_option == 1:
                        # Settings
                        settings_menu()
                    elif selected_option == 2:
                        # How to Play
                        how_to_play_menu()
                    elif selected_option == 3:
                        # Exit
                        pygame.quit()
                        sys.exit()

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение названия игры
        title_text = menu_font.render('Ākēdo', True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        
        # Обновляем опции с учетом текущего языка
        options = [
            get_text('start_game'),
            get_text('settings'),
            get_text('how_to_play'),
            get_text('exit')
        ]

        # Отображение опций меню
        for i, option in enumerate(options):
            if i == selected_option:
                option_display = '> ' + option
            else:
                option_display = option
            option_text = font.render(option_display, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 240 + i * 50))
        
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        
def how_to_play_menu():
    how_to_play_running = True
    back_option = 'Press ESC to return to the main menu.'
    
    instructions = [
        get_text('how_to_play_title'),
        "",
        *localization[settings['language']]['how_to_play_instructions']
    ]

    while how_to_play_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    how_to_play_running = False

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение инструкций
        y_offset = SCREEN_HEIGHT // 2 - 250 # Начальная позиция по Y
        for line in instructions:
            if line == "How to Play":
                # Заголовок
                line_text = pygame.font.SysFont('Courier', 36).render(line, True, TEXT_COLOR)
            elif line == back_option:
                # Подсказка для возврата
                line_text = pygame.font.SysFont('Courier', 28).render(line, True, TEXT_COLOR)
            else:
                # Основные инструкции
                line_text = pygame.font.SysFont('Courier', 28).render(line, True, TEXT_COLOR)
            screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_offset))
            y_offset += 40  # Отступ между строками
            
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

def settings_menu():
    settings_running = True
    selected_option = 0
    options = [
        get_text('resolution'),
        get_text('fullscreen_mode'),
        get_text('music_volume'),
        get_text('hit_volume'),
        get_text('other_sounds_volume'),
        get_text('language'),
        get_text('back')
    ]

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
                    current_option = options[selected_option]
                    if current_option == get_text('resolution'):
                        change_resolution()
                    elif current_option == get_text('fullscreen_mode'):
                        settings['fullscreen'] = not settings['fullscreen']
                        apply_display_settings()
                    elif current_option == get_text('music_volume'):
                        adjust_volume('volume_music')
                    elif current_option == get_text('hit_volume'):
                        adjust_volume('volume_hits')
                    elif current_option == get_text('other_sounds_volume'):
                        adjust_volume('volume_other')
                    elif current_option == get_text('language'):
                        change_language()
                    elif current_option == get_text('back'):
                        settings_running = False
                        
        options = [
            get_text('resolution'),
            get_text('fullscreen_mode'),
            get_text('music_volume'),
            get_text('hit_volume'),
            get_text('other_sounds_volume'),
            get_text('language'),
            get_text('back')
        ]
                        
        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение заголовка меню настроек
        settings_title = pygame.font.SysFont('Courier', 48).render(get_text('settings'), True, TEXT_COLOR)
        screen.blit(settings_title, (SCREEN_WIDTH // 2 - settings_title.get_width() // 2, 150))

        # Отображение опций настроек с текущими значениями
        for i, option in enumerate(options):
            if option == get_text('fullscreen_mode'):
                status = get_text('on') if settings['fullscreen'] else get_text('off')
                option_display = f"{option}: {status}"
            elif option == get_text('resolution'):
                option_display = f"{option}: {settings['resolution'][0]}x{settings['resolution'][1]}"
            elif option in [get_text('music_volume'), get_text('hit_volume'), get_text('other_sounds_volume')]:
                volume_key_map = {
                    get_text('music_volume'): 'volume_music',
                    get_text('hit_volume'): 'volume_hits',
                    get_text('other_sounds_volume'): 'volume_other'
                }
                volume_value = int(settings[volume_key_map[option]] * 100)
                option_display = f"{option}: {volume_value}%"
            elif option == get_text('language'):
                lang_display = 'English' if settings['language'] == 'en' else 'Русский'
                option_display = f"{option}: {lang_display}"
            else:
                option_display = option

            if i == selected_option:
                option_display = '> ' + option_display
            option_text = font.render(option_display, True, TEXT_COLOR)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 230 + i * 50))
            
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

def change_resolution():
    # Получаем текущее разрешение экрана пользователя
    infoObject = pygame.display.Info()
    current_display_resolution = (infoObject.current_w, infoObject.current_h)
    
    # Добавляем текущие разрешения и стандартные варианты
    resolutions = [
        (1280, 720),
        (1366, 768),
        (1600, 768),
        (1600, 900),
        (1776, 1000),
        (1920, 1080),
        (2048, 1152),
        (1856, 1392),
        (2560, 1440),
        (3440, 1440),
        (3840, 2160),
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

        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))

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
                    settings[volume_key] = max(0.0, settings[volume_key] - 0.05)
                    apply_volume_settings()
                elif event.key == pygame.K_RIGHT:
                    settings[volume_key] = min(1.0, settings[volume_key] + 0.05)
                    apply_volume_settings()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    adjusting = False

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Отображение текущего уровня громкости
        volume_value = int(settings[volume_key] * 100)
        # Определение ключа для локализации
        volume_key_map = {
            'volume_music': 'music_volume',
            'volume_hits': 'hit_volume',
            'volume_other': 'other_sounds_volume'
        }

        volume_text = font.render(f"{get_text(volume_key_map.get(volume_key, volume_key))}: {volume_value}%", True, TEXT_COLOR)
        screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)

        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        
def change_language():
    languages = ['en', 'ru']
    lang_names = {
        'en': 'English',
        'ru': 'Русский'
    }
    current_lang_index = languages.index(settings['language']) if settings['language'] in languages else 0
    
    changing_language = True
    
    while changing_language:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_lang_index = (current_lang_index - 1) % len(languages)
                elif event.key == pygame.K_RIGHT:
                    current_lang_index = (current_lang_index + 1) % len(languages)
                elif event.key == pygame.K_RETURN:
                    settings['language'] = languages[current_lang_index]
                    save_settings(settings)
                    changing_language = False
                elif event.key == pygame.K_ESCAPE:
                    changing_language = False
        
        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)
        
        # Отображение текущего выбора языка
        language_text = get_text('language')
        selected_lang = lang_names[languages[current_lang_index]]
        display_text = f"{language_text}: {selected_lang}"
        lang_display = font.render(display_text, True, TEXT_COLOR)
        screen.blit(lang_display, (SCREEN_WIDTH // 2 - lang_display.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Применение VHS эффектов
        chromatic_surface = chromatic_aberration(screen.copy())
        apply_scanlines(chromatic_surface)
        
        # Наложение VHS эффекта на экран
        chromatic_surface.blit(chromatic_surface, (0, 0))
        screen.blit(chromatic_surface, (0, 0))
        
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
    cursor_symbol = font.render('`', True, cursor_color)
    running = True
    esc_hold_start_time = None  # Время начала удержания клавиши Esc
    esc_hold_duration = 1000    # Время в миллисекундах для выхода в меню
    esc_pressed_during_pause = False  # Флаг, указывающий, что Esc был нажат во время паузы
    boss_appearance_number = 1  # Счетчик появлений босса
    pause_initialized = False

    while running:
        delta_time = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not paused:
                        paused = True
                        esc_hold_start_time = None  # Сбрасываем время удержания
                        esc_pressed_during_pause = False
                    else:
                        esc_hold_start_time = pygame.time.get_ticks()  # Начинаем отсчет удержания
                        esc_pressed_during_pause = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    if paused and esc_pressed_during_pause:
                        hold_time = pygame.time.get_ticks() - esc_hold_start_time if esc_hold_start_time else 0
                        if hold_time < esc_hold_duration:
                            # Короткое нажатие, отжимаем паузу
                            paused = False
                            pause_initialized = False
                        # Сбрасываем флаги
                        esc_hold_start_time = None
                        esc_pressed_during_pause = False

        if not paused:
            screen.fill(BACKGROUND_COLOR)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player.move(mouse_x, mouse_y)

            # Отображение персонажа игрока
            draw_text(PLAYER_SYMBOL, font, PLAYER_COLOR, int(player.x), int(player.y))
            screen.blit(cursor_symbol, (mouse_x - cursor_symbol.get_width() // 2, mouse_y - cursor_symbol.get_height() // 2))

            if not enemies:
                if player.hp > 0:
                    wave_countdown()
                    wave_start_time = pygame.time.get_ticks()
                    # Проверяем, является ли текущая волна боссовой
                    if wave % 10 == 5:
                        in_boss_fight = True
                        # Останавливаем основную музыку
                        pygame.mixer.music.stop()
                        # Воспроизводим музыку босса
                        if not music_channel.get_busy():
                            music_channel.play(boss_music, -1)
                        # Спавним босса
                        boss = Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, boss_appearance_number)
                        enemies.append(boss)
                        boss_appearance_number += 1
                    else:
                        in_boss_fight = False
                        # Обычный спавн врагов
                        enemies = spawn_enemies(wave * INITIAL_ENEMY_COUNT, wave)
                    wave += 1
                else:
                    pygame.mixer.Sound.play(game_over_sound)
                    game_over_text = pygame.font.SysFont('Courier', 48).render(get_text('game_over'), True, TEXT_COLOR)
                    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                    
                    # Применение VHS эффектов
                    chromatic_surface = chromatic_aberration(screen.copy())
                    apply_scanlines(chromatic_surface)

                    # Наложение VHS эффекта на экран
                    chromatic_surface.blit(chromatic_surface, (0, 0))
                    screen.blit(chromatic_surface, (0, 0))
                    
                    pygame.display.flip()
                    time.sleep(2)
                    return  # Возврат в главное меню

            # Обновление и отображение врагов и снарядов
            for enemy in enemies:
                enemy.move_towards_player(player.x, player.y, enemies)
                if isinstance(enemy, Boss):
                    enemy.update(delta_time, player.x, player.y, projectiles)
                    symbol = enemy.symbol
                    # Проверка состояния босса для отображения цвета
                    if enemy.is_red:
                        color = ENEMY_COLOR  # Красный цвет
                    else:
                        color = enemy.color
                    draw_text(symbol, boss_font, color, enemy.x, enemy.y)
                elif isinstance(enemy, RusherEnemy):
                    enemy.update(player.x, player.y, delta_time)
                    draw_text(enemy.symbol, font, enemy.color, int(enemy.x), int(enemy.y))
                else:
                    enemy.update(delta_time)
                    if not enemy.is_dead:
                        if isinstance(enemy, SuicideEnemy):
                            symbol = enemy.symbol
                        else:
                            if enemy.is_shooter:
                                projectile = enemy.shoot(player.x, player.y)
                                if projectile:
                                    projectiles.append(projectile)
                                symbol = SHOOTER_SYMBOL
                            else:
                                symbol = ENEMY_SYMBOL
                        draw_text(symbol, font, enemy.color, enemy.x, enemy.y)
                        
            # Отображение полоски здоровья босса
            for enemy in enemies:
                if isinstance(enemy, Boss):
                    # Размеры полоски HP
                    bar_width = SCREEN_WIDTH * 0.6
                    bar_height = 18
                    bar_x = (SCREEN_WIDTH - bar_width) / 2
                    bar_y = SCREEN_HEIGHT - bar_height - 30  # Отступ от нижнего края

                    # Рисуем белую рамку
                    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)  # Толщина рамки 1 пиксель

                    # Вычисляем ширину заполненной части
                    filled_width = (bar_width - 2) * (enemy.hp / enemy.max_hp)  # Вычитаем 2 пикселя для учёта рамки
                    if filled_width < 0:
                        filled_width = 0  # Чтобы не было отрицательной ширины

                    # Рисуем заполненную часть
                    pygame.draw.rect(screen, (162, 68, 43), (bar_x + 1, bar_y + 1, filled_width, bar_height - 2))

                    # Отображаем текст "Boss" над полоской HP
                    boss_text = font.render(get_text('boss'), True, (255, 255, 255))
                    text_rect = boss_text.get_rect(center=(SCREEN_WIDTH / 2, bar_y - 10))
                    screen.blit(boss_text, text_rect)
                    break  # Босс только один
                    
            for enemy in enemies[:]:
                if enemy.is_dead and isinstance(enemy, SuicideEnemy):
                    if enemy.explode:
                        # Воспроизводим звук взрыва или выстрела
                        if not shooter_fire_channel.get_busy():
                            shooter_fire_channel.play(shooter_fire_sound)
                        
                        # Враг взрывается и выпускает снаряды
                        num_projectiles = min(6 + enemy.wave, 12)
                        angle_between_projectiles = 360 / num_projectiles
                        for i in range(num_projectiles):
                            angle = math.radians(i * angle_between_projectiles)
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                            projectile = Projectile(enemy.x, enemy.y, dx, dy, enemy.damage)
                            projectiles.append(projectile)
                    enemies.remove(enemy)  # Удаляем врага из списка

            for projectile in projectiles[:]:
                if not projectile.update(player.x, player.y):
                    projectiles.remove(projectile)
                else:
                    projectile.draw(screen)

            # Обработка столкновений и проверка на окончание игры
            game_over = handle_collisions(player, enemies, damage_numbers, wave, wave_start_time, projectiles, health_pickups)
            if game_over:
                pygame.mixer.Sound.play(game_over_sound)
                game_over_text = pygame.font.SysFont('Courier', 48).render(get_text('game_over'), True, TEXT_COLOR)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                
                # Применение VHS эффектов
                chromatic_surface = chromatic_aberration(screen.copy())
                apply_scanlines(chromatic_surface)

                # Наложение VHS эффекта на экран
                chromatic_surface.blit(chromatic_surface, (0, 0))
                screen.blit(chromatic_surface, (0, 0))
                
                pygame.display.flip()
                time.sleep(2)

                # Если игрок погиб во время боя с боссом, останавливаем музыку босса и запускаем обычную
                if in_boss_fight:
                    in_boss_fight = False
                    boss_music.stop()
                    pygame.mixer.music.play(-1, 0.0)

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
                    healed_amount = player.health_pickup_heal_amount
                    player.heal(healed_amount)
                    health_pickups.remove(health_pickup)
                    pygame.mixer.Sound.play(health_pickup_sound)
                    damage_numbers.append(DamageNumber(player.x, player.y, f"+{healed_amount} {get_text('hp')}", (0, 255, 0)))

            # Отображение статистики игрока (уровень, здоровье и опыт)
            stats_text = f"{get_text('level')}: {player.level}  {get_text('hp')}: {player.hp:.1f}/{player.max_hp:.1f}  {get_text('defense')}: {player.defense_upgrade_count * 0.2:.1f}  {get_text('exp')}: {player.exp:.1f}/{player.exp_to_level_up}"
            draw_text(stats_text, font, TEXT_COLOR, 10, 10)

            # Удаление мертвых врагов
            enemies = [enemy for enemy in enemies if not enemy.is_dead]
            
            if not enemies:
                if in_boss_fight:
                    in_boss_fight = False
                    # Останавливаем музыку босса
                    boss_music.stop()
                    # Запускаем основную музыку
                    pygame.mixer.music.play(-1, 0.0)

            # Применение VHS эффектов
            chromatic_surface = chromatic_aberration(screen.copy())
            apply_scanlines(chromatic_surface)

            # Наложение VHS эффекта на экран
            chromatic_surface.blit(chromatic_surface, (0, 0))
            screen.blit(chromatic_surface, (0, 0))

            pygame.display.flip()
        else:
            if not pause_initialized:
                pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                # Отображаем паузу
                screen.blit(pause_overlay, (0, 0))
                pause_font = pygame.font.SysFont('Courier', 48)
                pause_text_surface = pause_font.render(get_text('paused'), True, TEXT_COLOR)
                pause_text_surface.set_alpha(200)  # Прозрачность текста
                # Отображение текста в центре экрана
                screen.blit(pause_text_surface, 
                            (SCREEN_WIDTH // 2 - pause_text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                hint_font = pygame.font.SysFont('Courier', 28)
                hint_text_surface = hint_font.render(get_text('hold_to_menu'), True, TEXT_COLOR)
                hint_text_surface.set_alpha(200)
                screen.blit(hint_text_surface, 
                            (SCREEN_WIDTH // 2 - hint_text_surface.get_width() // 2, SCREEN_HEIGHT - 100))
                chromatic_surface = chromatic_aberration(screen.copy())
                apply_scanlines(chromatic_surface)
                chromatic_surface.blit(chromatic_surface, (0, 0))
                screen.blit(chromatic_surface, (0, 0))
                pause_initialized = True

            pygame.display.flip()

            # Проверка удержания клавиши Esc для выхода в меню
            if esc_hold_start_time is not None:
                hold_time = pygame.time.get_ticks() - esc_hold_start_time
                if hold_time >= esc_hold_duration:
                    if in_boss_fight:
                        in_boss_fight = False
                        boss_music.stop()
                        pygame.mixer.music.play(-1, 0.0)
                    return  # Возвращаемся из функции main(), что приведет к возврату в главное меню

    pygame.quit()

if __name__ == "__main__":
    while True:
        main_menu()
        main()
