import pygame
import sys
import math
import random
import argparse

# python fractal_forest.py   --width 800 --height 600  --depth 8 12  --length 10   --spread 10 50   --count 7   --size 0.6 1.2

def generate_branches(x, y, angle, depth, branch_length, angle_spread, rnd):
    """
    Recursively yield one branch segment at a time:
      (x_start, y_start, x_end, y_end, thickness)
    Uses the provided random.Random instance for reproducible angles.
    """
    if depth == 0:
        return
    length = depth * branch_length
    rad = math.radians(angle)
    x2 = x + math.cos(rad) * length
    y2 = y + math.sin(rad) * length
    thickness = max(1, depth // 2)
    yield (x, y, x2, y2, thickness)

    # random spreads for left and right
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
    p = argparse.ArgumentParser(description="Animated fractal tree in Pygame")
    p.add_argument("--width",   type=int,   default=800,                 help="Window width")
    p.add_argument("--height",  type=int,   default=600,                 help="Window height")
    p.add_argument("--bg",      type=int,   nargs=3, default=(0, 0, 0),  metavar=('R','G','B'),
                   help="Background color")
    p.add_argument("--branch",  type=int,   nargs=3, default=(255,255,255), metavar=('R','G','B'),
                   help="Branch color")
    p.add_argument("--depth",   type=int,   default=10,                  help="Max recursion depth")
    p.add_argument("--length",  type=int,   default=8,                   help="Base branch length multiplier")
    p.add_argument("--spread",  type=float, nargs=2, default=(15,45),    metavar=('MIN','MAX'),
                   help="Angle spread range in degrees")
    return p.parse_args()

def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode((args.width, args.height))
    pygame.display.set_caption("Fractal Tree – Always Within Bounds")
    clock = pygame.time.Clock()

    running = True
    while running:
        # pick a seed so bounding and drawing use the same random angles
        seed = random.randrange(2**32)
        rnd_sim = random.Random(seed)
        rnd_draw = random.Random(seed)

        # 1) Simulate with branch_length=1 to get bounding box
        segments = list(generate_branches(
            0, 0, -90, args.depth,
            1, tuple(args.spread), rnd_sim
        ))
        xs = [coord for seg in segments for coord in (seg[0], seg[2])]
        ys = [coord for seg in segments for coord in (seg[1], seg[3])]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width_range  = max_x - min_x
        height_range = max_y - min_y

        # 2) Compute safe_length so tree fits 90% of the canvas
        width_scale  = float('inf') if width_range == 0  else (args.width  * 0.9) / width_range
        height_scale = float('inf') if height_range == 0 else (args.height * 0.9) / height_range
        safe_length  = min(args.length, width_scale, height_scale)

        # 3) Clear screen
        screen.fill(tuple(args.bg))

        # 4) Prepare the actual draw generator
        gen = generate_branches(
            args.width // 2, args.height,
            -90, args.depth,
            safe_length, tuple(args.spread),
            rnd_draw
        )

        reset = False
        drawing = True

        # 5) Animate growth
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

            try:
                x1, y1, x2, y2, th = next(gen)
                pygame.draw.line(screen,
                                 tuple(args.branch),
                                 (x1, y1), (x2, y2), th)
                pygame.display.flip()
            except StopIteration:
                drawing = False

            clock.tick(60)

        if not running:
            break
        if reset:
            continue  # immediately start over with a fresh tree

        # 6) Finished drawing: wait for Enter (reset) or Space (quit)
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
