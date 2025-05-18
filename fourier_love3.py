import pygame
import numpy as np
import math
import sys

# ── KONFIGURASI ─────────────────────────────────────────────────────────────
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
FPS                        = 30
NUM_SAMPLES                = 1000   # jumlah titik sampel pada kurva
TIME_SCALE                 = 1     # multiplier kecepatan animasi
SCALE_X                    = -1    # flip horizontal jika perlu
SCALE_Y                    = -1    # flip vertikal untuk orientasi
SCALE_FACTOR               = 15    # skala (zoom) epicycle

# ── FUNGSI PARAMETRIK HATI ─────────────────────────────────────────────────
def heart_parametric(t):
    x = 16 * math.sin(t)**3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return complex(x, y)

# ── SAMPEL KURVA HATI ───────────────────────────────────────────────────────
ts = np.linspace(0, 2 * math.pi, NUM_SAMPLES, endpoint=False)
pts = np.array([heart_parametric(t) for t in ts])

# ── HITUNG KOEFISIEN FOURIER ────────────────────────────────────────────────
coeffs = np.fft.fft(pts) / NUM_SAMPLES
freqs  = np.fft.fftfreq(NUM_SAMPLES, d=1/NUM_SAMPLES)
fourier = sorted(
    [(f, abs(c), np.angle(c)) for f, c in zip(freqs, coeffs)],
    key=lambda x: x[1], reverse=True
)
NUM_CIRCLES = len(fourier)  # untuk ditampilkan di layar

# ── INISIALISASI PYGAME ─────────────────────────────────────────────────────
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fourier Pen: Draw Heart Shape – Enter Reset, Space Quit")
clock  = pygame.time.Clock()

# ── STATE ANIMASI ──────────────────────────────────────────────────────────
time_val = 0.0
dt       = (2 * math.pi / NUM_SAMPLES) * TIME_SCALE
path     = []
running  = True
CENTER   = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

# ── LOOP UTAMA ─────────────────────────────────────────────────────────────
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = False
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                time_val = 0.0
                path.clear()

    screen.fill((30, 30, 30))  # latar gelap

    # ── GAMBARKAN TEKS JUMLAH EPICYCLES
    info_text = font.render(f"Epicycles: {NUM_CIRCLES}", True, (255, 255, 255))
    screen.blit(info_text, (10, 10))

    # ── GAMBARKAN EPICYCLES (UNDERLAY), SEPERTI MEKANISME PEN
    x0, y0 = CENTER
    for freq, amp, phase in fourier:
        x1 = x0 + SCALE_X * amp * math.cos(freq * time_val + phase) * SCALE_FACTOR
        y1 = y0 + SCALE_Y * amp * math.sin(freq * time_val + phase) * SCALE_FACTOR
        pygame.draw.circle(screen, (80, 80, 80), (int(x0), int(y0)), int(amp * SCALE_FACTOR), 1)
        pygame.draw.line(screen, (150, 150, 150), (int(x0), int(y0)), (int(x1), int(y1)), 2)
        x0, y0 = x1, y1

    # ── GAMBARKAN JALUR HATI (OVERLAY) DI TITIK EPICYCLES
    tip = (int(x0), int(y0))
    path.insert(0, tip)
    if len(path) > NUM_SAMPLES:
        path.pop()
    if len(path) > 1:
        pygame.draw.lines(screen, (220, 20, 60), False, path, 2)

    # ── UPDATE WAKTU DAN ULANGI
    time_val += dt
    if time_val > 2 * math.pi:
        time_val = 0.0
        path.clear()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()