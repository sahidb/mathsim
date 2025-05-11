import pygame
import random
import math
import sys
import matplotlib.pyplot as plt

# Monte Carlo PI Simulation with Auto-Stop, Manual Stop, and Convergence Plot
# ---------------------------------------------------------------------------
# The simulation runs until:
#   - The user presses SPACE (manual stop)
#   - A maximum number of trials (AUTO_STOP_TRIALS) is reached

# Screen settings
WIDTH, HEIGHT = 600, 600
RADIUS = WIDTH // 2
CX, CY = WIDTH // 2, HEIGHT // 2
RECORD_EVERY = 1000       # record PI estimate every N trials
AUTO_STOP_TRIALS = 50000  # set to 0 to disable auto-stop

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)


def init_pygame():
    """Initialize Pygame and return screen, font, and clock."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Monte Carlo PI Simulation (SPACE to stop)")
    font = pygame.font.SysFont("Arial", 18)
    clock = pygame.time.Clock()
    return screen, font, clock


def draw_static(screen):
    """Draw static square border, circle outline, and stop instruction."""
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 1)
    pygame.draw.circle(screen, BLACK, (CX, CY), RADIUS, 1)
    instr = pygame.font.SysFont("Arial", 14).render(
        f"SPACE: manual stop | AUTO_STOP_TRIALS={AUTO_STOP_TRIALS}", True, BLACK)
    screen.blit(instr, (10, HEIGHT - 20))
    pygame.display.flip()


def generate_point():
    """Generate a random point within the square."""
    return random.uniform(0, WIDTH), random.uniform(0, HEIGHT)


def is_inside_circle(x, y):
    """Return True if (x, y) lies within the circle."""
    return math.hypot(x - CX, y - CY) <= RADIUS


def draw_point(screen, x, y, inside):
    """Plot a point: green if inside, red if outside."""
    screen.set_at((int(x), int(y)), GREEN if inside else RED)


def update_text(screen, font, inside_points, total_points):
    """Update onscreen text with the latest PI estimate and trial count."""
    pi_est = 4 * inside_points / total_points if total_points else 0
    pygame.draw.rect(screen, WHITE, (10, 10, 300, 20))
    txt = font.render(f"PI ≈ {pi_est:.6f} | Trials: {total_points}", True, BLACK)
    screen.blit(txt, (10, 10))
    pygame.display.flip()


def main():
    screen, font, clock = init_pygame()
    draw_static(screen)

    total_points = inside_points = 0
    trials, estimates = [], []
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Auto-stop check
        if AUTO_STOP_TRIALS > 0 and total_points >= AUTO_STOP_TRIALS:
            break

        # Monte Carlo sampling
        x, y = generate_point()
        inside = is_inside_circle(x, y)
        total_points += 1
        inside_points += inside

        draw_point(screen, x, y, inside)
        update_text(screen, font, inside_points, total_points)

        # Record periodic estimate
        if total_points % RECORD_EVERY == 0:
            estimates.append(4 * inside_points / total_points)
            trials.append(total_points)

        clock.tick(0)

    pygame.quit()

    # Plot convergence
    plt.plot(trials, estimates, label='Estimate')
    plt.axhline(math.pi, linestyle='--', label='True PI')
    plt.xlabel('Trials')
    plt.ylabel('Estimated PI')
    plt.title('PI Convergence via Monte Carlo')
    plt.legend()
    plt.show()

    sys.exit()

if __name__ == "__main__":
    main()
