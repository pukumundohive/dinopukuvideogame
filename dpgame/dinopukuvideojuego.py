import pygame
import sys
import os
import random

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Desplazamiento Lateral")

# Reloj para controlar la velocidad del juego
clock = pygame.time.Clock()

# Función para cargar y escalar imágenes manteniendo la proporción
def load_and_scale(image_path, target_height=None, full_screen=False):
    try:
        image = pygame.image.load(image_path)
        if full_screen:
            return pygame.transform.scale(image, (WIDTH, HEIGHT))
        elif target_height:
            original_width, original_height = image.get_size()
            scale_factor = target_height / original_height
            new_width = int(original_width * scale_factor)
            return pygame.transform.scale(image, (new_width, target_height))
        return image
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen '{image_path}'.")
        sys.exit()

# Cargar imágenes
try:
    start_screen = load_and_scale("start_screen.png", full_screen=True)
    background = load_and_scale("background.png", HEIGHT)
    run_frames = [load_and_scale("run_1.png", 120), load_and_scale("run_2.png", 120), load_and_scale("run_3.png", 120)]
    jump_frame = load_and_scale("jump.png", 120)  # Misma altura que las demás imágenes
    duck_frame = load_and_scale("duck.png", 60)
    obstacle_images = [load_and_scale(f"obstacle_{i}.png", 80) for i in range(1, 7)]  # Obstáculos escalados
    coin1_image = load_and_scale("coin.png", 30)  # Moneda normal (HBD Coins)
    coin2_image = load_and_scale("coin2.png", 40)  # Moneda especial (HivePower)
    end_screen = load_and_scale("end_screen.png", full_screen=True)  # Pantalla final
    airplane_banner = load_and_scale("airplane_banner.png", 100)  # Avión con banner
except Exception as e:
    print(f"Error al cargar imágenes: {e}")
    sys.exit()

# Cargar sonidos
try:
    jump_sound = pygame.mixer.Sound("jump_sound.wav")
    run_sound = pygame.mixer.Sound("run_sound.wav")
    coin_sound = pygame.mixer.Sound("coin_sound.wav")
    pygame.mixer.music.load("background_music.mp3")  # Música de fondo
    pygame.mixer.music.set_volume(0.4)  # Ajustar volumen
    pygame.mixer.music.play(-1)  # Reproducir en bucle
except Exception as e:
    print(f"Error al cargar sonidos: {e}")

# Variables del avión con banner
airplane_x = WIDTH  # Comienza fuera de la pantalla (lado derecho)
airplane_y = random.randint(50, 150)  # Altura aleatoria en el cielo
airplane_speed = 5  # Velocidad del avión (más rápida)
airplane_active = False  # Controla si el avión está activo
airplane_timer = 0  # Temporizador para activar el avión

# Mostrar la pantalla de inicio
def show_start_screen():
    screen.blit(start_screen, (0, 0))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Botón izquierdo del mouse
                waiting = False

# Mostrar la pantalla de inicio
show_start_screen()

# Variables del personaje
x = WIDTH // 8
y = HEIGHT - 150
velocity_y = 0
gravity = 0.8
jump_power = -12
on_ground = False
is_ducking = False

# Variables de animación
current_frame = 0
frame_delay = 10
frame_counter = 0

# Variables de scroll
scroll = 0
max_scroll_speed = 5

# Plataforma (suelo)
platform = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)

# Obstáculos y monedas
obstacles = []
coins1 = []  # Monedas normales (HBD Coins)
coins2 = []  # Monedas especiales (HivePower)
spawn_timer = 0
spawn_interval = 120
coin1_spawn_timer = 0
coin1_spawn_interval = 180
coin2_spawn_timer = 0
coin2_spawn_interval = 300
coin1_count = 0
coin2_count = 0

# Tiempo para que aparezcan las monedas especiales (1 minuto)
time_to_coin2 = 60

# Estado del juego
game_started = True
start_time = pygame.time.get_ticks()

# Fuente futurista para los contadores
try:
    font = pygame.font.Font("future_font.ttf", 24)
except FileNotFoundError:
    font = pygame.font.SysFont("Arial", 24, bold=True)

# Bucle principal del juego
running = True
game_won = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Control de teclas
    if keys[pygame.K_RIGHT] and not game_won:
        frame_counter += 1
        if frame_counter >= frame_delay:
            frame_counter = 0
            current_frame = (current_frame + 1) % len(run_frames)
        scroll += max_scroll_speed
    else:
        current_frame = 0

    if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground and not is_ducking and not game_won:
        velocity_y = jump_power
        on_ground = False
        jump_sound.play()  # Sonido de salto

    if keys[pygame.K_DOWN] and not game_won:
        is_ducking = True
    else:
        is_ducking = False

    # Aplicar gravedad
    if not game_won:
        velocity_y += gravity
        y += velocity_y

    # Verificar colisión con el suelo
    if y + run_frames[0].get_height() >= platform.y:
        y = platform.y - run_frames[0].get_height()
        velocity_y = 0
        on_ground = True

    # Scroll lateral automático
    background_width = background.get_width()
    if scroll > background_width - WIDTH:
        scroll = 0

    # Generar obstáculos
    if not game_won:
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            obstacle_image = random.choice(obstacle_images)
            obstacle_rect = obstacle_image.get_rect()
            obstacle_rect.x = WIDTH
            obstacle_rect.y = HEIGHT - 130
            obstacles.append((obstacle_image, obstacle_rect))

    # Generar monedas normales
    if not game_won:
        coin1_spawn_timer += 1
        if coin1_spawn_timer >= coin1_spawn_interval:
            coin1_spawn_timer = 0
            coin1_rect = coin1_image.get_rect()
            coin1_rect.x = WIDTH
            coin1_rect.y = random.randint(HEIGHT - 250, HEIGHT - 100)
            coins1.append(coin1_rect)

    # Generar monedas especiales (después de 1 minuto)
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    if elapsed_time >= time_to_coin2 and not game_won:
        coin2_spawn_timer += 1
        if coin2_spawn_timer >= coin2_spawn_interval:
            coin2_spawn_timer = 0
            coin2_rect = coin2_image.get_rect()
            coin2_rect.x = WIDTH
            coin2_rect.y = random.randint(HEIGHT - 250, HEIGHT - 100)
            coins2.append(coin2_rect)

    # Mover obstáculos
    for i, (obstacle_image, obstacle_rect) in enumerate(obstacles):
        obstacle_rect.x -= max_scroll_speed
        obstacles[i] = (obstacle_image, obstacle_rect)

    # Mover monedas normales
    for i, coin1_rect in enumerate(coins1):
        coin1_rect.x -= max_scroll_speed
        coins1[i] = coin1_rect

    # Mover monedas especiales
    for i, coin2_rect in enumerate(coins2):
        coin2_rect.x -= max_scroll_speed
        coins2[i] = coin2_rect

    # Eliminar elementos fuera de la pantalla
    obstacles = [(img, rect) for img, rect in obstacles if rect.x + rect.width > 0]
    coins1 = [coin1_rect for coin1_rect in coins1 if coin1_rect.x + coin1_rect.width > 0]
    coins2 = [coin2_rect for coin2_rect in coins2 if coin2_rect.x + coin2_rect.width > 0]

    # Colisiones con monedas normales
    character_rect = pygame.Rect(x, y, run_frames[0].get_width(), run_frames[0].get_height())
    for coin1_rect in coins1[:]:
        if character_rect.colliderect(coin1_rect):
            coins1.remove(coin1_rect)
            coin1_count += 1
            coin_sound.play()  # Sonido de recolección de monedas

    # Colisiones con monedas especiales
    for coin2_rect in coins2[:]:
        if character_rect.colliderect(coin2_rect):
            coins2.remove(coin2_rect)
            coin2_count += 1
            coin_sound.play()  # Sonido de recolección de monedas

    # Verificar si el jugador ha ganado
    if coin1_count >= 47 and coin2_count >= 15:
        game_won = True

    # Actualizar animación
    if is_ducking:
        current_image = duck_frame
        y = HEIGHT - 100
    elif not on_ground:
        current_image = jump_frame
    elif keys[pygame.K_RIGHT]:
        current_image = run_frames[current_frame]
    else:
        current_image = run_frames[0]

    # Dibujar elementos
    screen.fill((0, 0, 0))
    screen.blit(background, (-scroll, 0))
    screen.blit(background, (background_width - scroll, 0))
    pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 50, WIDTH, 50))

    # Dibujar obstáculos
    for obstacle_image, obstacle_rect in obstacles:
        screen.blit(obstacle_image, obstacle_rect.topleft)

    # Dibujar monedas normales
    for coin1_rect in coins1:
        screen.blit(coin1_image, coin1_rect.topleft)

    # Dibujar monedas especiales
    for coin2_rect in coins2:
        screen.blit(coin2_image, coin2_rect.topleft)

    # Dibujar personaje
    screen.blit(current_image, (x, y))

    # Mostrar contador de monedas normales (HBD Coins)
    coin1_text = font.render(f"HBD Coins: {coin1_count}/47", True, (255, 255, 255))
    screen.blit(coin1_text, (10, 10))

    # Mostrar contador de monedas especiales (Hive Power)
    coin2_text = font.render(f"Hive Power: {coin2_count}/15", True, (255, 255, 255))
    screen.blit(coin2_text, (10, 40))

    # Simular el movimiento del avión con banner
    airplane_timer += 1
    if airplane_timer > 600:  # Aparece cada ~10 segundos (ajusta según sea necesario)
        airplane_active = True
        airplane_timer = 0

    if airplane_active:
        airplane_x -= airplane_speed  # Mover el avión hacia la izquierda
        rotated_banner = pygame.transform.flip(airplane_banner, True, False)  # Rotación tipo "espejo" horizontal
        screen.blit(rotated_banner, (airplane_x, airplane_y))
        if airplane_x < -rotated_banner.get_width():  # Cuando el avión sale de la pantalla
            airplane_x = WIDTH  # Reiniciar posición
            airplane_y = random.randint(50, 150)  # Altura aleatoria
            airplane_active = False

    # Mostrar la pantalla final si el jugador ha ganado
    if game_won:
        screen.blit(end_screen, (0, 0))  # Mostrar la pantalla final
        pygame.display.flip()
        pygame.time.wait(5000)  # Esperar 5 segundos antes de cerrar el juego
        running = False

    # Actualizar pantalla
    pygame.display.flip()
    clock.tick(60)

# Salir del juego
pygame.quit()
sys.exit()