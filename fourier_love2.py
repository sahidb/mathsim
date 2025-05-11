import pygame
import numpy as np
import math
import sys

# ── Konfigurasi ─────────────────────────────────────────────────────────────
LEBAR, TINGGI       = 800, 600
FPS                  = 10
JUMLAH_SAMPEL        = 500       # jumlah titik sampel pada kurva
SKALA_WAKTU          = 1         # pengali kecepatan animasi
SKALA_X              = -1        # flip horizontal (jaga orientasi)
SKALA_Y              = -1        # flip vertikal (perbaiki orientasi)
A                    = 15        # skala (zoom) untuk lingkaran epicycle
MARGIN               = 10        # jarak tepi agar epicycles tidak keluar canvas

# ── Fungsi hati parametris sebagai angka kompleks─────────────────────────────
def empatier_hati(t):
    x = 16 * np.sin(t)**3
    y = 13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)
    return complex(x, y)

# ── Sampel titik kurva hati ──────────────────────────────────────────────────
ts    = np.linspace(0, 2*math.pi, JUMLAH_SAMPEL, endpoint=False)
pts   = np.array([empatier_hati(t) for t in ts])

# ── Hitung DFT dan koefisien Fourier───────────────────────────────────────────
coeffs = np.fft.fft(pts) / JUMLAH_SAMPEL
freqs  = np.fft.fftfreq(JUMLAH_SAMPEL, d=1/JUMLAH_SAMPEL)

koefisien_fourier = [(f, abs(c), np.angle(c)) for f, c in zip(freqs, coeffs)]
# urutkan berdasarkan amplitudo menurun
koefisien_fourier.sort(key=lambda x: x[1], reverse=True)

# ── Hitung penempatan agar tidak overflow─────────────────────────────────────
# Margin dari tepi
MARGIN = 10  
# Penempatan epicycles di kiri
max_amp = max(amp for _, amp, _ in koefisien_fourier)
CENTER_CIRCLES = (int(max_amp * A + MARGIN), TINGGI // 2)
# Hitung batas x mentah dari fungsi hati
heart_raw = np.array([empatier_hati(t) for t in ts])
heart_x   = SKALA_X * heart_raw.real * A
# Hitung offset sehingga bentuk hati berada dalam batas dan di samping epicycles
x_min = heart_x.min()
offset_x_path = int(-x_min + MARGIN)
CENTER_PATH    = (offset_x_path, 0)

# ── Inisialisasi Pygame ────────────────────────────────────────────────────── ──────────────────────────────────────────────────────
pygame.init()
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Animasi Fourier: Bentuk Hati – Enter Reset, Space Quit")
jam   = pygame.time.Clock()

# ── Status animasi ───────────────────────────────────────────────────────────
waktu = 0.0
dt    = (2 * math.pi / JUMLAH_SAMPEL) * SKALA_WAKTU
jalur = []

# ── Loop utama ───────────────────────────────────────────────────────────────
berjalan = True
while berjalan:
    for peristiwa in pygame.event.get():
        if peristiwa.type == pygame.QUIT:
            berjalan = False
        elif peristiwa.type == pygame.KEYDOWN:
            if peristiwa.key == pygame.K_SPACE:
                berjalan = False  # quit
            elif peristiwa.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                waktu = 0         # reset
                jalur.clear()

    layar.fill((30, 30, 30))

    # ── Gambar epicycles ─────────────────────────────────────────────────────
    x0, y0 = CENTER_CIRCLES
    for frek, amp, fase in koefisien_fourier:
        x1 = x0 + SKALA_X * amp * math.cos(frek * waktu + fase) * A
        y1 = y0 + SKALA_Y * amp * math.sin(frek * waktu + fase) * A

        # lingkaran dan vektor
        pygame.draw.circle(layar, (100, 100, 100), (int(x0), int(y0)), int(amp * A), 1)
        pygame.draw.line(layar, (200, 200, 200), (int(x0), int(y0)), (int(x1), int(y1)), 2)
        x0, y0 = x1, y1

    # ── Rekam dan gambar jejak path───────────────────────────────────────────
    ujung = (x0 + CENTER_PATH[0], y0 + CENTER_PATH[1])
    jalur.insert(0, ujung)
    if len(jalur) > JUMLAH_SAMPEL:
        jalur.pop()
    if len(jalur) > 1:
        pygame.draw.lines(layar, (220, 20, 60), False, jalur, 2)

    # ── Update waktu dan looping ─────────────────────────────────────────────
    waktu += dt
    if waktu > 2 * math.pi:
        waktu = 0
        jalur.clear()

    pygame.display.flip()
    jam.tick(FPS)

pygame.quit()
sys.exit()
