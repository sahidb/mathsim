import pygame
import numpy as np
import math
import sys

# ── Konfigurasi ─────────────────────────────────────────────────────────────
LEBAR, TINGGI       = 800, 600
FPS                  = 60
JUMLAH_SAMPEL        = 200       # jumlah titik sampel pada kurva
SKALA_WAKTU          = 1         # pengali kecepatan animasi
SKALA_X              = -1        # -1 untuk flip horizontal (biarkan agar bentuk hati tidak terbalik horizontal)
SKALA_Y              = -1        # -1 untuk flip vertikal (memperbaiki orientasi vertikal)
A                    = 15        # skala (zoom) untuk lingkaran epicycle
TITIK_PUSAT          = (200, 300)
PENGGESER_GAMBAR     = (400, 0)  # offset menggambar jejak

# ── Fungsi hati parametris sebagai angka kompleks─────────────────────────────
def empatier_hati(t):
    x = 16 * np.sin(t)**3
    y = 13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)
    return complex(x, y)

# ── Sampel titik kurva hati ──────────────────────────────────────────────────
ts   = np.linspace(0, 2*math.pi, JUMLAH_SAMPEL, endpoint=False)
pts  = np.array([empatier_hati(t) for t in ts])

# ── Hitung DFT dan bangun daftar koefisien Fourier────────────────────────────
coeffs = np.fft.fft(pts) / JUMLAH_SAMPEL
freqs  = np.fft.fftfreq(JUMLAH_SAMPEL, d=1/JUMLAH_SAMPEL)

koefisien_fourier = []
for f, c in zip(freqs, coeffs):
    amplitudo = abs(c)
    fase      = np.angle(c)
    koefisien_fourier.append((f, amplitudo, fase))
# urutkan berdasarkan amplitudo menurun agar lingkaran terbesar digambar pertama
koefisien_fourier.sort(key=lambda x: x[1], reverse=True)

# ── Inisialisasi Pygame ──────────────────────────────────────────────────────
pygame.init()
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Animasi Fourier: Bentuk Hati – Enter Reset, Space Quit")
jam   = pygame.time.Clock()

# ── Status animasi ───────────────────────────────────────────────────────────
waktu = 0.0
dt    = (2*math.pi / JUMLAH_SAMPEL) * SKALA_WAKTU
jalur = []

# ── Loop utama ───────────────────────────────────────────────────────────────
berjalan = True
while berjalan:
    for peristiwa in pygame.event.get():
        if peristiwa.type == pygame.QUIT:
            berjalan = False
        elif peristiwa.type == pygame.KEYDOWN:
            if peristiwa.key == pygame.K_SPACE:
                # keluar saat tekan Space
                berjalan = False
            elif peristiwa.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                # reset animasi saat Enter
                waktu = 0
                jalur.clear()

    layar.fill((30, 30, 30))  # latar gelap

    # ── Gambar epicycle ──────────────────────────────────────────────────────
    x0, y0 = TITIK_PUSAT
    for frek, amp, fase in koefisien_fourier:
        # titik akhir vektor dengan flip horizontal dan vertikal
        x1 = x0 + SKALA_X * amp * math.cos(frek * waktu + fase) * A
        y1 = y0 + SKALA_Y * amp * math.sin(frek * waktu + fase) * A

        # lingkaran epicycle
        pygame.draw.circle(layar, (100,100,100), (int(x0), int(y0)), int(amp*A), 1)
        # garis vektor
        pygame.draw.line(layar, (200,200,200), (int(x0), int(y0)), (int(x1), int(y1)), 2)

        x0, y0 = x1, y1

    # ── Rekam ujung vektor dan gambar jejak ───────────────────────────────────
    ujung = (x0 + PENGGESER_GAMBAR[0], y0 + PENGGESER_GAMBAR[1])
    jalur.insert(0, ujung)
    if len(jalur) > JUMLAH_SAMPEL:
        jalur.pop()

    if len(jalur) > 1:
        pygame.draw.lines(layar, (220,20,60), False, jalur, 2)

    # ── Perbarui waktu dan ulangi saat t > 2π ─────────────────────────────────
    waktu += dt
    if waktu > 2*math.pi:
        waktu = 0
        jalur.clear()

    pygame.display.flip()
    jam.tick(FPS)

pygame.quit()
sys.exit()