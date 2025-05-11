import pygame
import cupy as cp
import numpy as np
import math
import sys

# ── KONFIGURASI ─────────────────────────────────────────────────────────────
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS                        = 60
NUM_CIRCLES                = 10000   # jumlah epicycles
time_scale                 = 1.0     # pengali kecepatan animasi
SCALE_X                    = -1      # flip horizontal jika perlu
SCALE_Y                    = -1      # flip vertikal untuk orientasi
SCALE_FACTOR               = 0.05    # skala (zoom) epicycle

# ── PARAMETRIK HATI ─────────────────────────────────────────────────────────
# Sample dasar untuk DFT
SAMPLE_POINTS = 200
ts = np.linspace(0, 2 * math.pi, SAMPLE_POINTS, endpoint=False)
pts = np.array([complex(
    16 * math.sin(t)**3,
    13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
) for t in ts])

# Hitung koefisien Fourier pada CPU
coeffs = np.fft.fft(pts) / SAMPLE_POINTS
freqs = np.fft.fftfreq(SAMPLE_POINTS, d=1/SAMPLE_POINTS)
amps  = np.abs(coeffs)
phases = np.angle(coeffs)

# Perluas atau tile ke jumlah epicycle yang diinginkan
freqs = np.tile(freqs, int(np.ceil(NUM_CIRCLES / SAMPLE_POINTS)))[:NUM_CIRCLES]
amps  = np.tile(amps,  int(np.ceil(NUM_CIRCLES / SAMPLE_POINTS)))[:NUM_CIRCLES]
phases = np.tile(phases, int(np.ceil(NUM_CIRCLES / SAMPLE_POINTS)))[:NUM_CIRCLES]

# Pindahkan semua ke GPU
freqs_dev  = cp.array(freqs, dtype=cp.float64)
amps_dev   = cp.array(amps,  dtype=cp.float64)
phases_dev = cp.array(phases, dtype=cp.float64)

time_val = 0.0
dt = (2 * math.pi / NUM_CIRCLES) * time_scale
path = []
running = True
CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

# Inisialisasi Pygame
game = pygame
game.init()
screen = game.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game.display.set_caption("CuPy GPU Fourier: 10000 Epicycles – Enter Reset, Space Quit")
clock = game.time.Clock()

while running:
    for ev in game.event.get():
        if ev.type == game.QUIT:
            running = False
        elif ev.type == game.KEYDOWN:
            if ev.key == game.K_SPACE:
                running = False
            elif ev.key in (game.K_RETURN, game.K_KP_ENTER):
                time_val = 0.0
                path.clear()

    screen.fill((30, 30, 30))

    # Hitung posisi dx, dy di GPU via CuPy
    angles = freqs_dev * time_val + phases_dev
    dx_dev = cp.cos(angles) * amps_dev
    dy_dev = cp.sin(angles) * amps_dev

    # Pindahkan hasil ke host untuk menggambar
    dx = cp.asnumpy(dx_dev)
    dy = cp.asnumpy(dy_dev)

    # Gambar epicycles dan penjejakan
    x0, y0 = CENTER
    for i in range(NUM_CIRCLES):
        x1 = x0 + SCALE_X * dx[i] * SCALE_FACTOR
        y1 = y0 + SCALE_Y * dy[i] * SCALE_FACTOR
        game.draw.circle(screen, (50,50,50), (int(x0), int(y0)), int(abs(dx[i])*SCALE_FACTOR), 1)
        game.draw.line(screen,   (100,100,100), (int(x0), int(y0)), (int(x1), int(y1)), 1)
        x0, y0 = x1, y1

    # Gambar path
    tip = (int(x0), int(y0))
    path.insert(0, tip)
    if len(path) > NUM_CIRCLES:
        path.pop()
    if len(path) > 1:
        game.draw.lines(screen, (220,20,60), False, path, 2)

    # Update waktu dan looping
    time_val += dt
    if time_val > 2 * math.pi:
        time_val = 0.0
        path.clear()

    game.display.flip()
    clock.tick(FPS)

game.quit()
sys.exit()
