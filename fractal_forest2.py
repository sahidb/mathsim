import pygame
import sys
import math
import random
import argparse

def generate_branches(x, y, angle, depth, branch_length, angle_spread, rnd):
    """
    Hasilkan setiap segmen ranting satu per satu:
      (x_awal, y_awal, x_akhir, y_akhir, ketebalan)
    Menggunakan objek random.Random rnd untuk konsistensi.
    """
    if depth == 0:
        return
    length = depth * branch_length
    rad = math.radians(angle)
    x2 = x + math.cos(rad) * length
    y2 = y + math.sin(rad) * length
    thickness = max(1, depth // 2)
    yield (x, y, x2, y2, thickness)

    spread_l = rnd.uniform(angle_spread[0], angle_spread[1])
    spread_r = rnd.uniform(angle_spread[0], angle_spread[1])

    yield from generate_branches(
        x2, y2, angle - spread_l, depth - 1,
        branch_length, angle_spread, rnd
    )
    yield from generate_branches(
        x2, y2, angle + spread_r, depth - 1,
        branch_length, angle_spread, rnd
    )

def parse_args():
    parser = argparse.ArgumentParser(
        description="Hutan fractal animasi dengan kedalaman, jarak, ukuran, posisi, dan mode warna"
    )
    parser.add_argument("--width",   type=int,   default=800,
                        help="Lebar jendela (piksel)")
    parser.add_argument("--height",  type=int,   default=600,
                        help="Tinggi jendela (piksel)")
    parser.add_argument("--bg",      type=int,   nargs=3, default=(0, 0, 0),
                        metavar=('R','G','B'),
                        help="Warna latar belakang (RGB)")
    parser.add_argument("--branch",  type=int,   nargs=3, default=(255,255,255),
                        metavar=('R','G','B'),
                        help="Warna default ranting (RGB) saat mode white")
    parser.add_argument("--depth",   type=int,   nargs=2, default=(10,10),
                        metavar=('MIN','MAKS'),
                        help="Rentang kedalaman rekursi (min dan maks)")
    parser.add_argument("--length",  type=int,   default=8,
                        help="Panjang dasar ranting")
    parser.add_argument("--spread",  type=float, nargs=2, default=(15,45),
                        metavar=('MIN','MAKS'),
                        help="Rentang sudut cabang (derajat)")
    parser.add_argument("--count",   type=int,   default=5,
                        help="Jumlah pohon dalam hutan")
    parser.add_argument("--size",    type=float, nargs=2, default=(0.5,1.0),
                        metavar=('MIN','MAKS'),
                        help="Faktor ukuran relatif tiap pohon (0.0–1.0)")
    parser.add_argument("--color-mode", choices=["white","random"], default="white",
                        help="Mode warna ranting: white (semua satu warna) atau random (acak tiap pohon)")
    return parser.parse_args()


def main():
    args = parse_args()
    depth_min, depth_max = args.depth

    pygame.init()
    screen = pygame.display.set_mode((args.width, args.height))
    pygame.display.set_caption("Hutan Fractal – Enter=Reset • Space=Keluar")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Siapkan generator dan warna per pohon
        tree_data = []  # list of (generator, warna)
        for _ in range(args.count):
            seed = random.randrange(2**32)
            rnd_sim = random.Random(seed)
            rnd_draw = random.Random(seed)

            depth_i = rnd_draw.randint(depth_min, depth_max)
            size_factor = rnd_draw.uniform(args.size[0], args.size[1])

            # Simulasi bounding box untuk depth_i
            segs = list(generate_branches(0, 0, -90, depth_i, 1, tuple(args.spread), rnd_sim))
            xs = [c for seg in segs for c in (seg[0], seg[2])]
            ys = [c for seg in segs for c in (seg[1], seg[3])]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w_range = max_x - min_x
            h_range = max_y - min_y

            # hitung safe_length
            w_scale = float('inf') if w_range == 0 else (args.width * 0.9) / w_range
            h_scale = float('inf') if h_range == 0 else (args.height * 0.9) / h_range
            safe_length = min(args.length, w_scale, h_scale) * size_factor

            # rentang X acak dengan margin 5%
            margin_x = args.width * 0.05
            x_min = margin_x - min_x * safe_length
            x_max = args.width - margin_x - max_x * safe_length
            x_pos = rnd_draw.uniform(x_min, x_max)
            y_pos = args.height

            # tentukan warna ranting berdasarkan mode
            if args.color_mode == "white":
                warna = tuple(args.branch)
            else:
                warna = (rnd_draw.randint(0,255), rnd_draw.randint(0,255), rnd_draw.randint(0,255))

            gen = generate_branches(x_pos, y_pos, -90, depth_i, safe_length, tuple(args.spread), rnd_draw)
            tree_data.append((gen, warna))

        screen.fill(tuple(args.bg))
        reset = False
        drawing = True

        # Animasi setiap pohon paralel
        while running and drawing:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
                    drawing = False
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_SPACE:
                        running = False
                        drawing = False
                    elif evt.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        reset = True
                        drawing = False

            if not drawing:
                break

            any_active = False
            for gen, warna in tree_data:
                try:
                    x1, y1, x2, y2, th = next(gen)
                    pygame.draw.line(screen, warna, (x1, y1), (x2, y2), th)
                    any_active = True
                except StopIteration:
                    continue

            pygame.display.flip()
            if not any_active:
                drawing = False
            clock.tick(60)

        if not running:
            break
        if reset:
            continue

        # Tunggu reset atau keluar
        waiting = True
        while running and waiting:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
                    waiting = False
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_SPACE:
                        running = False
                        waiting = False
                    elif evt.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        waiting = False
            clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
