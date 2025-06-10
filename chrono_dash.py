import asyncio
import platform
import pygame
import random
import numpy as np
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrono Dash")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Player settings
player_size = 30
player_speed = 5
player_pos = [100, HEIGHT // 2]

# Gate settings
gate_width = 50
gate_height = 100
gates = []
gate_spawn_rate = 100
gate_spawn_counter = 0

# Obstacle settings
obstacle_size = 40
obstacle_base_speed = 3
obstacles = []
obstacle_spawn_rate = 80
obstacle_spawn_counter = 0

# Score and font
score = 0
font = pygame.font.SysFont("arial", 24)

# Sound setup (NumPy for Pyodide compatibility)
sample_rate = 44100
duration = 0.1
t = np.linspace(0, duration, int(sample_rate * duration))
sound_array = np.sin(2 * np.pi * 660 * t) * 32767
sound_array = np.column_stack((sound_array, sound_array)).astype(np.int16)
collect_sound = pygame.sndarray.make_sound(sound_array)

# Game state
running = True
game_over = False
clock = pygame.time.Clock()
FPS = 60

def setup():
    global gates, obstacles, score, player_pos, running, game_over, obstacle_base_speed
    gates = []
    obstacles = []
    score = 0
    player_pos = [100, HEIGHT // 2]
    running = True
    game_over = False
    obstacle_base_speed = 3
    for _ in range(3):
        spawn_gate()
        spawn_obstacle()

def spawn_gate():
    y = random.randint(gate_height // 2, HEIGHT - gate_height // 2)
    gates.append([WIDTH, y, random.uniform(0, 2 * math.pi)])  # Add phase for blinking

def spawn_obstacle():
    y = random.randint(obstacle_size // 2, HEIGHT - obstacle_size // 2)
    obstacles.append([WIDTH, y, random.uniform(0, 2 * math.pi)])

def update_loop():
    global running, game_over, score, obstacle_base_speed, gate_spawn_counter, obstacle_spawn_counter

    if not running:
        return

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                setup()

    if game_over:
        return

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed
    player_pos[1] = max(player_size // 2, min(HEIGHT - player_size // 2, player_pos[1]))

    # Spawn gates and obstacles
    gate_spawn_counter += 1
    if gate_spawn_counter >= gate_spawn_rate:
        spawn_gate()
        gate_spawn_counter = 0

    obstacle_spawn_counter += 1
    if obstacle_spawn_counter >= obstacle_spawn_rate:
        spawn_obstacle()
        obstacle_spawn_counter = 0

    # Update gates
    for gate in gates[:]:
        gate[0] -= 3  # Move left
        gate[2] += 0.1  # Update phase for blinking
        if gate[0] < -gate_width:
            gates.remove(gate)

    # Update obstacles
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_base_speed
        obstacle[1] += math.sin(obstacle[2]) * 3  # Sinusoidal movement
        obstacle[2] += 0.05
        if obstacle[0] < -obstacle_size:
            obstacles.remove(obstacle)

    # Collision detection
    player_rect = pygame.Rect(player_pos[0] - player_size // 2, player_pos[1] - player_size // 2, player_size, player_size)
    for gate in gates[:]:
        gate_rect = pygame.Rect(gate[0] - gate_width // 2, gate[1] - gate_height // 2, gate_width, gate_height)
        if player_rect.colliderect(gate_rect):
            gates.remove(gate)
            score += 10
            collect_sound.play()
            spawn_gate()

    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle[0] - obstacle_size // 2, obstacle[1] - obstacle_size // 2, obstacle_size, obstacle_size)
        if player_rect.colliderect(obstacle_rect):
            game_over = True
            break

    # Increase difficulty
    score += 0.1
    obstacle_base_speed = 3 + score / 1000

    # Draw everything
    screen.fill(BLACK)
    # Draw player
    pygame.draw.rect(screen, WHITE, (player_pos[0] - player_size // 2, player_pos[1] - player_size // 2, player_size, player_size))
    # Draw gates with blinking effect
    for gate in gates:
        alpha = (math.sin(gate[2]) + 1) / 2 * 255
        color = (0, min(255, int(alpha)), 0)
        pygame.draw.rect(screen, color, (gate[0] - gate_width // 2, gate[1] - gate_height // 2, gate_width, gate_height))
    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.circle(screen, RED, (int(obstacle[0]), int(obstacle[1])), obstacle_size // 2)
    # Draw score
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    # Draw game over
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

async def main():
    setup()
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
