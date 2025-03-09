import pygame
import sys
import os
import random

# Set the asset directory path
ASSET_DIR = "dpgame"

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Desplazamiento Lateral")

# Reloj para controlar la velocidad del juego
clock = pygame.time.Clock()

# Flag to control sound - can be turned off for better performance
ENABLE_SOUND = True

# Speed control - set to True for better performance
PERFORMANCE_MODE = True

# Función para cargar y escalar imágenes manteniendo la proporción
def load_and_scale(image_path, target_height=None, full_screen=False):
    try:
        # Modify path to include asset directory
        full_path = os.path.join(ASSET_DIR, image_path)
        print(f"Loading image from: {full_path}")
        image = pygame.image.load(full_path)
        if full_screen:
            return pygame.transform.scale(image, (WIDTH, HEIGHT))
        elif target_height:
            original_width, original_height = image.get_size()
            scale_factor = target_height / original_height
            new_width = int(original_width * scale_factor)
            return pygame.transform.scale(image, (new_width, target_height))
        return image
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen '{full_path}'.")
        # Create a colored placeholder image instead of returning None
        placeholder = pygame.Surface((50, 50) if not target_height else (50, target_height))
        placeholder.fill((255, 0, 255))  # Magenta for visibility
        return placeholder

# Cargar recursos del juego
try:
    # Load the font with correct path and fallback
    try:
        font_path = os.path.join(ASSET_DIR, "future-font.TTF")
        print(f"Loading font from: {font_path}")
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, 36)
            small_font = pygame.font.Font(font_path, 24)
        else:
            print(f"Font file not found, using default font")
            font = pygame.font.SysFont("Arial", 36)
            small_font = pygame.font.SysFont("Arial", 24)
    except Exception as e:
        print(f"Error loading custom font: {e}, using default font")
        font = pygame.font.SysFont("Arial", 36)
        small_font = pygame.font.SysFont("Arial", 24)
    
    # Load and scale images
    # Load start screen with better quality (no scaling to maintain quality)
    try:
        start_screen_path = os.path.join(ASSET_DIR, "start_screen.png") 
        print(f"Loading high quality start screen from: {start_screen_path}")
        start_screen_raw = pygame.image.load(start_screen_path).convert_alpha()
        # Scale to screen size but use better quality scaling method
        start_screen = pygame.transform.smoothscale(start_screen_raw, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Error loading high quality start screen: {e}")
        # Fallback to normal scaling if smoothscale fails
        start_screen = load_and_scale("start_screen.png", full_screen=True)
    background = load_and_scale("background.png", HEIGHT)
    run_frames = [load_and_scale("run_1.png", 120), load_and_scale("run_2.png", 120), load_and_scale("run_3.png", 120)]
    jump_frame = load_and_scale("jump.png", 120)  # Misma altura que las demás imágenes
    duck_frame = load_and_scale("duck.png", 60)
    obstacle_images = [load_and_scale(f"obstacle_{i}.png", 80) for i in range(1, 7)]  # Obstáculos escalados
    coin1_image = load_and_scale("coin.png", 30)  # Moneda normal (HBD Coins)
    coin2_image = load_and_scale("coin2.png", 40)  # Moneda especial (HivePower)
    # Load end screen with better quality (no scaling to maintain quality)
    try:
        end_screen_path = os.path.join(ASSET_DIR, "end_screen.png") 
        print(f"Loading high quality end screen from: {end_screen_path}")
        end_screen_raw = pygame.image.load(end_screen_path).convert_alpha()
        # Scale to screen size but use better quality scaling method
        end_screen = pygame.transform.smoothscale(end_screen_raw, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Error loading high quality end screen: {e}")
        # Fallback to normal scaling if smoothscale fails
        end_screen = load_and_scale("end_screen.png", full_screen=True)
    airplane_banner = load_and_scale("airplane_banner.png", 150)  # Avión con banner (más grande para mejor visibilidad)
    
    # Create dummy sound class for when sound is disabled
    class DummySound:
        def play(self): pass
    
    # Load sounds with correct paths with better error handling
    if ENABLE_SOUND:
        try:
            jump_sound_path = os.path.join(ASSET_DIR, "jump_sound.wav")
            print(f"Loading sound from: {jump_sound_path}")
            jump_sound = pygame.mixer.Sound(jump_sound_path)
            
            run_sound_path = os.path.join(ASSET_DIR, "run_sound.wav")
            print(f"Loading sound from: {run_sound_path}")
            run_sound = pygame.mixer.Sound(run_sound_path)
            
            coin_sound_path = os.path.join(ASSET_DIR, "coin_sound.wav")
            print(f"Loading sound from: {coin_sound_path}")
            coin_sound = pygame.mixer.Sound(coin_sound_path)
            
            music_path = os.path.join(ASSET_DIR, "background_music.mp3")
            print(f"Loading music from: {music_path}")
            pygame.mixer.music.load(music_path)  # Música de fondo
            pygame.mixer.music.set_volume(0.4)  # Ajustar volumen
            pygame.mixer.music.play(-1)  # Reproducir en bucle
            print("Sound enabled and loaded successfully")
        except Exception as e:
            print(f"Error loading sound files: {e}")
            # Use dummy sound objects for error handling
            jump_sound = run_sound = coin_sound = DummySound()
    else:
        print("Sound disabled for better performance")
        jump_sound = run_sound = coin_sound = DummySound()
    
except Exception as e:
    print(f"Error al cargar recursos: {e}")
    pygame.quit()
    sys.exit()

# Constantes del juego
GRAVITY = 1
JUMP_STRENGTH = -16
GAME_SPEED = 5
GROUND_HEIGHT = HEIGHT - 40

# Estado del juego
game_state = "START"  # START, PLAYING, GAME_OVER
score = 0
high_score = 0
hbd_coins = 0  # HBD Coins counter
hive_power = 0  # HivePower counter

# ====== Resto del código del archivo original a partir de aquí ======

# Función para mostrar la pantalla de inicio
def show_start_screen():
    screen.blit(start_screen, (0, 0))
    start_text = font.render("Presiona ESPACIO para comenzar", True, (255, 255, 255))
    text_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    screen.blit(start_text, text_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Función para mostrar la pantalla de game over
def show_game_over_screen():
    global high_score
    
    # Actualizar puntuación máxima si es necesario
    if score > high_score:
        high_score = score
    
    screen.blit(end_screen, (0, 0))
    game_over_text = font.render("GAME OVER", True, (255, 255, 255))
    score_text = font.render(f"Puntuación: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"Mejor Puntuación: {high_score}", True, (255, 255, 255))
    
    # Mostrar HBD Coins y HivePower recolectados
    hbd_text = small_font.render(f"HBD Coins: {hbd_coins}", True, (0, 200, 0))  # Color verde
    hive_text = small_font.render(f"HivePower: {hive_power}", True, (220, 20, 60))  # Color rojo carmesí
    
    restart_text = font.render("Presiona ESPACIO para reiniciar", True, (255, 255, 255))
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 70))
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 - 20))
    
    # Mostrar contadores de monedas con sus iconos
    # HBD Coins
    screen.blit(pygame.transform.scale(coin1_image, (20, 20)), (WIDTH//2 - 100, HEIGHT//2 + 30))
    screen.blit(hbd_text, (WIDTH//2 - 70, HEIGHT//2 + 30))
    
    # HivePower
    screen.blit(pygame.transform.scale(coin2_image, (25, 25)), (WIDTH//2 - 100, HEIGHT//2 + 60))
    screen.blit(hive_text, (WIDTH//2 - 70, HEIGHT//2 + 60))
    
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 120))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    return False

# Clase para el personaje
class Character:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = 100
        self.y = GROUND_HEIGHT - 120  # Posición inicial sobre el suelo
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.run_animation_count = 0
        self.animation_speed = 5  # Frames entre cambios de animación
        self.frame_counter = 0
        self.rect = pygame.Rect(self.x + 20, self.y + 20, 80, 100)  # Colisión ajustada
    
    def update(self):
        # Aplicar gravedad
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Limitar al suelo
        if self.y > GROUND_HEIGHT - 120 and not self.is_ducking:
            self.y = GROUND_HEIGHT - 120
            self.vel_y = 0
            self.is_jumping = False
        
        # Limitar el personaje agachado al suelo
        if self.is_ducking:
            if self.y > GROUND_HEIGHT - 60:  # Posición más baja para agacharse
                self.y = GROUND_HEIGHT - 60
                self.vel_y = 0
                self.is_jumping = False
        
        # Actualizar el rectángulo de colisión según el estado
        if self.is_ducking:
            self.rect = pygame.Rect(self.x + 20, self.y + 10, 80, 50)  # Colisión más baja al agacharse
        else:
            self.rect = pygame.Rect(self.x + 20, self.y + 20, 80, 100)  # Colisión normal
    
    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True
            jump_sound.play()
    
    def duck(self, ducking):
        # Si está saltando, no puede agacharse
        if self.is_jumping:
            return
            
        self.is_ducking = ducking
        
        # Reproducir sonido al agacharse/levantarse
        if ducking:
            run_sound.play()
    
    def draw(self):
        if self.is_jumping:
            screen.blit(jump_frame, (self.x, self.y))
        elif self.is_ducking:
            screen.blit(duck_frame, (self.x, self.y))
        else:
            # Animación de correr
            self.frame_counter += 1
            if self.frame_counter >= self.animation_speed:
                self.run_animation_count = (self.run_animation_count + 1) % 3
                self.frame_counter = 0
                
                # Reproducir sonido de correr en cada cambio de frame
                if self.run_animation_count == 0:
                    run_sound.play()
                    
            screen.blit(run_frames[self.run_animation_count], (self.x, self.y))

# Clase para los obstáculos
class Obstacle:
    def __init__(self, x, image_idx=None):
        self.x = x
        # Si no se especifica un índice de imagen, elegir uno aleatorio
        if image_idx is None:
            self.image_idx = random.randint(0, 5)
        else:
            self.image_idx = image_idx
        self.image = obstacle_images[self.image_idx]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.x, GROUND_HEIGHT - self.height, self.width, self.height)
    
    def update(self):
        self.x -= GAME_SPEED
        self.rect.x = self.x
    
    def draw(self):
        screen.blit(self.image, (self.x, GROUND_HEIGHT - self.height))
    
    def is_off_screen(self):
        return self.x + self.width < 0

# Clase para monedas (HBD Coins y HivePower)
class Coin:
    def __init__(self, x, y, special=False):
        self.x = x
        self.y = y
        self.special = special  # True = HivePower (roja), False = HBD Coin (amarilla)
        self.coin_type = "HivePower" if special else "HBD Coin"
        self.image = coin2_image if special else coin1_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.collected = False
        self.value = 5 if special else 1  # HivePower vale más puntos que las HBD Coins
    
    def update(self):
        self.x -= GAME_SPEED
        self.rect.x = self.x
    
    def draw(self):
        if not self.collected:
            screen.blit(self.image, (self.x, self.y))
    
    def is_off_screen(self):
        return self.x + self.width < 0

# Clase para el avión con el banner
class Airplane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = airplane_banner
        self.speed = 3  # Más lento que los obstáculos
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.passed = False
    
    def update(self):
        self.x -= self.speed
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))
    
    def is_off_screen(self):
        return self.x + self.width < 0

# Función principal del juego
def main_game():
    global game_state, score, hbd_coins, hive_power
    
    # Reiniciar puntuación y contadores de monedas
    score = 0
    hbd_coins = 0
    hive_power = 0
    
    # Crear objetos del juego
    character = Character()
    obstacles = []
    coins = []
    airplanes = []
    
    # Contadores y temporizadores
    obstacle_timer = 0
    coin_timer = 0
    airplane_timer = 0
    score_timer = 0
    last_special_coin = 0  # Tiempo desde la última moneda especial
    
    # Variables para controlar la dificultad
    game_speed_increase = 0.001  # Incremento gradual de velocidad
    current_game_speed = GAME_SPEED
    background_x = 0  # Para el scroll del fondo
    
    # Bucle principal del juego
    running = True
    while running:
        # Control de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    character.jump()
                elif event.key == pygame.K_DOWN:
                    character.duck(True)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    character.duck(False)
        
        # Actualizar el personaje
        character.update()
        
        # Performance mode makes the game run faster
        if PERFORMANCE_MODE:
            # Skip some frames for better performance
            pygame.time.delay(10)  # Reduce CPU usage
            
            # Make obstacles and coins appear less frequently but move faster
            current_game_speed = GAME_SPEED * 1.5
        else:
            # Normal speed mode
            # Aumentar la velocidad del juego progresivamente
            current_game_speed += game_speed_increase
        
        # Generar obstáculos periódicamente
        obstacle_timer += 1
        if obstacle_timer >= random.randint(60, 120):  # Entre 1 y 2 segundos a 60 FPS
            new_x = WIDTH + random.randint(50, 150)
            obstacles.append(Obstacle(new_x))
            obstacle_timer = 0
        
        # Generar monedas periódicamente
        coin_timer += 1
        if coin_timer >= random.randint(30, 90):  # Entre 0.5 y 1.5 segundos
            new_x = WIDTH + random.randint(20, 100)
            new_y = random.randint(GROUND_HEIGHT - 100, GROUND_HEIGHT - 40)  # Altura variable
            
            # Decidir si es una moneda especial (más rara)
            special = False
            if last_special_coin > 600:  # Al menos 10 segundos desde la última moneda especial
                special = random.random() < 0.2  # 20% de probabilidad
                if special:
                    last_special_coin = 0
            
            coins.append(Coin(new_x, new_y, special))
            coin_timer = 0
        
        last_special_coin += 1
        
        # Generar aviones con banner ocasionalmente (más frecuente ahora)
        airplane_timer += 1
        if airplane_timer >= random.randint(200, 400):  # Mucho más frecuente para mejor visibilidad
            new_x = WIDTH + 100
            new_y = random.randint(50, 150)  # Altura aleatoria pero por la parte superior
            airplanes.append(Airplane(new_x, new_y))
            airplane_timer = 0
        
        # Actualizar obstáculos y comprobar colisiones
        for obstacle in obstacles[:]:
            obstacle.update()
            
            # Comprobar colisión con el personaje
            if character.rect.colliderect(obstacle.rect):
                game_state = "GAME_OVER"
                running = False
            
            if obstacle.is_off_screen():
                obstacles.remove(obstacle)
        
        # Actualizar monedas y comprobar colecciones
        for coin in coins[:]:
            coin.update()
            
            # Comprobar si el personaje recoge la moneda
            if not coin.collected and character.rect.colliderect(coin.rect):
                coin.collected = True
                score += coin.value
                
                # Incrementar contador específico según el tipo de moneda
                if coin.special:
                    hive_power += 1  # HivePower (moneda especial)
                else:
                    hbd_coins += 1  # HBD Coins (moneda normal)
                    
                coin_sound.play()
            
            if coin.is_off_screen() or coin.collected:
                coins.remove(coin)
        
        # Actualizar aviones
        for airplane in airplanes[:]:
            airplane.update()
            
            # Marcar si el avión ha pasado por la pantalla (para dar puntos)
            if not airplane.passed and airplane.x < character.x:
                airplane.passed = True
                score += 2  # Puntos por pasar por debajo del avión
            
            if airplane.is_off_screen():
                airplanes.remove(airplane)
        
        # Aumentar la puntuación con el tiempo
        score_timer += 1
        if score_timer >= 30:  # Cada medio segundo
            score += 1
            score_timer = 0
        
        # ===== Dibujar escena =====
        
        # Fondo con parallax scrolling
        background_x -= current_game_speed * 0.5  # Más lento que los obstáculos
        if background_x <= -background.get_width():
            background_x = 0
            
        screen.blit(background, (background_x, 0))
        screen.blit(background, (background_x + background.get_width(), 0))
        
        # Dibujar línea del suelo
        pygame.draw.line(screen, (83, 56, 70), (0, GROUND_HEIGHT), (WIDTH, GROUND_HEIGHT), 2)
        
        # Dibujar obstáculos
        for obstacle in obstacles:
            obstacle.draw()
        
        # Dibujar monedas
        for coin in coins:
            coin.draw()
        
        # Dibujar aviones
        for airplane in airplanes:
            airplane.draw()
        
        # Dibujar personaje
        character.draw()
        
        # Mostrar puntuación y contadores de monedas
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        # Mostrar contadores de monedas HBD y HivePower con sus iconos
        # HBD Coins (verde)
        screen.blit(pygame.transform.scale(coin1_image, (20, 20)), (20, 60))
        hbd_text = small_font.render(f"HBD: {hbd_coins}", True, (0, 200, 0))  # Color verde
        screen.blit(hbd_text, (50, 60))
        
        # HivePower (rojas)
        screen.blit(pygame.transform.scale(coin2_image, (25, 25)), (20, 90))
        hive_text = small_font.render(f"HivePower: {hive_power}", True, (220, 20, 60))  # Color rojo carmesí
        screen.blit(hive_text, (50, 90))
        
        # Actualizar pantalla
        pygame.display.flip()
        
        # Controlar velocidad del juego
        clock.tick(60)

# Bucle principal
while True:
    if game_state == "START":
        show_start_screen()
        game_state = "PLAYING"
    
    elif game_state == "PLAYING":
        main_game()
    
    elif game_state == "GAME_OVER":
        if show_game_over_screen():
            game_state = "PLAYING"