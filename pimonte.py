import pygame
import random
import math
import sys

# Monte Carlo PI Simulation with Continuous In-Pygame Convergence Plot
# ---------------------------------------------------------------------
# Points appear in left panel; continuous convergence line in right panel.

# Settings
SIM_SIZE = 600           # Simulation square size
CIRCLE_SCALE = 0.8       # Circle scale factor (0<scale<=1)
GRAPH_WIDTH = 300        # Width of graph panel
WIDTH, HEIGHT = SIM_SIZE + GRAPH_WIDTH, SIM_SIZE
BASE_RADIUS = SIM_SIZE // 2
RADIUS = int(BASE_RADIUS * CIRCLE_SCALE)
CX, CY = BASE_RADIUS, BASE_RADIUS
AUTO_STOP_TRIALS = 150000 # 0 to disable auto-stop
# AUTO_STOP_TRIALS = 0 # 0 to disable auto-stop

# Graph axis bounds
y_min, y_max = 3.0, 3.3

# Colors
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Monte Carlo PI - SPACE to Stop")
    font = pygame.font.SysFont("Arial", 18)
    small_font = pygame.font.SysFont("Arial", 14)
    clock = pygame.time.Clock()
    return screen, font, small_font, clock


def draw_static(screen, small_font):
    # Simulation panel
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, 0, SIM_SIZE, SIM_SIZE), 1)
    pygame.draw.circle(screen, BLACK, (CX, CY), RADIUS, 1)
    # Graph panel background and axes
    graph_x = SIM_SIZE
    screen.fill(WHITE, (graph_x, 0, GRAPH_WIDTH, HEIGHT))
    pygame.draw.rect(screen, BLACK, (graph_x, 0, GRAPH_WIDTH, HEIGHT), 1)
    y_axis_x = graph_x + 40
    x_axis_y = HEIGHT - 30
    # Y axis
    pygame.draw.line(screen, BLACK, (y_axis_x, 10), (y_axis_x, x_axis_y), 2)
    # X axis
    pygame.draw.line(screen, BLACK, (y_axis_x, x_axis_y), (graph_x+GRAPH_WIDTH-10, x_axis_y), 2)
    # Y ticks & labels
    for val in (y_min, (y_min+y_max)/2, y_max):
        y = 10 + int((y_max-val)/(y_max-y_min)*(HEIGHT-40))
        pygame.draw.line(screen, BLACK, (y_axis_x-5, y), (y_axis_x+5, y), 1)
        lbl = small_font.render(f"{val:.2f}", True, BLACK)
        screen.blit(lbl, (graph_x+5, y-10))
    # True PI line
    pi_line_y = 10 + int((y_max-math.pi)/(y_max-y_min)*(HEIGHT-40))
    pygame.draw.line(screen, RED, (y_axis_x, pi_line_y), (graph_x+GRAPH_WIDTH-10, pi_line_y), 1)
    screen.blit(small_font.render("π", True, RED), (y_axis_x+5, pi_line_y-15))
    # Instructions
    screen.blit(small_font.render("SPACE to stop simulation", True, BLACK), (graph_x+10, HEIGHT-20))
    screen.blit(small_font.render(f"Auto-stop: {AUTO_STOP_TRIALS}", True, BLACK), (graph_x+10, HEIGHT-40))
    pygame.display.flip()


def generate_point():
    return random.uniform(0, SIM_SIZE), random.uniform(0, SIM_SIZE)


def is_inside(x, y):
    return math.hypot(x-CX, y-CY) <= RADIUS


def draw_point(screen, x, y, inside):
    screen.set_at((int(x), int(y)), GREEN if inside else RED)
    # update that pixel
    pygame.display.update((int(x), int(y), 1, 1))


def update_status(screen, font, inside_count, total_count):
    # Account for circle scaling: pi ≈ (inside/total)*(4/scale^2)
    factor = 4/(CIRCLE_SCALE**2)
    pi_est = inside_count/total_count*factor if total_count else 0
    screen.fill(WHITE, (10, 10, SIM_SIZE-20, 20))
    text = font.render(f"PI ≈ {pi_est:.6f} | Trials: {total_count}", True, BLACK)
    screen.blit(text, (10, 10))
    pygame.display.update((0, 0, SIM_SIZE, 40))
    return pi_est


def plot_graph_point(screen, small_font, pi_val, count, prev):
    # Continuous plotting using AUTO_STOP_TRIALS for x-scale
    if AUTO_STOP_TRIALS <= 0:
        return prev
    graph_x = SIM_SIZE
    y_axis_x = graph_x + 40
    # X coordinate
    x = y_axis_x + int((count/AUTO_STOP_TRIALS)*(GRAPH_WIDTH-60))
    # Y coordinate
    y = 10 + int((y_max-pi_val)/(y_max-y_min)*(HEIGHT-40))
    if prev is not None:
        pygame.draw.line(screen, BLUE, prev, (x, y), 1)
        # update around line
        rect = pygame.Rect(min(prev[0], x)-1, min(prev[1], y)-1,
                           abs(x-prev[0])+2, abs(y-prev[1])+2)
        pygame.display.update(rect)
    else:
        screen.set_at((x, y), BLUE)
        pygame.display.update((x, y, 1, 1))
    return (x, y)


def main():
    screen, font, small_font, clock = init_pygame()
    draw_static(screen, small_font)

    total = inside_count = 0
    prev_gp = None
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or \
               (ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE):
                running = False
        if AUTO_STOP_TRIALS and total >= AUTO_STOP_TRIALS:
            running = False

        if not running:
            break

        # Monte Carlo step
        x, y = generate_point()
        inside = is_inside(x, y)
        total += 1
        inside_count += inside

        draw_point(screen, x, y, inside)
        pi_est = update_status(screen, font, inside_count, total)
        prev_gp = plot_graph_point(screen, small_font, pi_est, total, prev_gp)

        clock.tick(0)

    # Pause until close or SPACE again
    paused = True
    while paused:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or \
               (ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE):
                paused = False
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
