import pygame
import random
import math
import sys
import colorsys
import numpy as np
from enum import Enum
import json, os

SAVEFILE = "savegame.json"

class GameState(Enum):
    MENU = 0
    PLAY = 1

class Background:
    """
    Procedurally generate one of six backgrounds:
      - "grass": a green field with random darker-green blades
      - "leaf_litter": a brownish base with random leaf/rock shapes
      - "sky": a sky-blue gradient with “cloud” blobs
      - "black": a plain black background
      - "birthday_picnic": a festive picnic scene with cake, balloons, food, etc.
      - "bathroom": a bathroom with sink, toilet, mirror, and scattered toiletries
    """
    STYLES = ["grass", "leaf_litter", "sky", "black", "birthday_picnic", "bathroom", "wild_flowers", "kitchen_counter"]

    def __init__(self, width, height, style=None):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

        # If style was passed and valid, use it; otherwise pick random
        if style in Background.STYLES:
            self.style = style
        else:
            self.style = random.choice(Background.STYLES)

        # Dispatch exactly as before
        if self.style == "grass":
            self._generate_grass()
        elif self.style == "leaf_litter":
            self._generate_leaf_litter()
        elif self.style == "sky":
            self._generate_sky()
        elif self.style == "black":
            self._generate_black()
        elif self.style == "birthday_picnic":
            self._generate_birthday_picnic()
        elif self.style == "bathroom":
            self._generate_bathroom()
        elif self.style == "wild_flowers":
            self._generate_wild_flowers()
        else:  # "kitchen_counter"
            self._generate_kitchen_counter()

    def _generate_grass(self):
        """Fill with green and draw random blades of grass."""
        base_green = (100, 180, 60)
        blade_green = (80, 160, 40)
        self.surface.fill(base_green)

        # Draw random “blades” as thin triangles
        for _ in range((self.width * self.height) // 500):
            x = random.randint(0, self.width)
            y = random.randint(self.height // 20, self.height)
            height = random.randint(10, 25)
            tilt = random.randint(-3, 3)
            points = [
                (x, y),
                (x + tilt + 1, y - height),
                (x + tilt - 1, y - height)
            ]
            pygame.draw.polygon(self.surface, blade_green, points)

    def _generate_leaf_litter(self):
        """Fill with earthy brown and draw random leaf/rock ellipses."""
        base_brown = (80, 50, 20)
        leaf_colors = [
            (120, 70, 20),
            (160, 100, 50),
            (100, 60, 15),
            (50, 30, 10)
        ]
        rock_colors = [
            (120, 120, 120),
            (150, 150, 150),
            (90, 90, 90)
        ]
        self.surface.fill(base_brown)

        # Scatter “leaves” (small, angled ellipses)
        for _ in range((self.width * self.height) // 10000):
            w = random.randint(10, 25)
            h = random.randint(5, 12)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            angle = random.uniform(0, 360)
            color = random.choice(leaf_colors)
            leaf_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surf, color, (0, 0, w, h))
            leaf_surf = pygame.transform.rotate(leaf_surf, angle)
            self.surface.blit(leaf_surf, (x, y))

        # Scatter “rocks” (gray circles)
        for _ in range((self.width * self.height) // 20000):
            r = random.randint(5, 15)
            x = random.randint(0, self.width - 2*r)
            y = random.randint(0, self.height - 2*r)
            color = random.choice(rock_colors)
            pygame.draw.circle(self.surface, color, (x + r, y + r), r)

    def _generate_sky(self):
        """Create a simple vertical gradient and a few fluffy cloud blobs."""
        top_color = (135, 206, 235)   # sky blue
        bottom_color = (80, 170, 200)  # deeper blue
        # Draw vertical gradient
        for y in range(self.height):
            frac = y / self.height
            r = top_color[0] + (bottom_color[0] - top_color[0]) * frac
            g = top_color[1] + (bottom_color[1] - top_color[1]) * frac
            b = top_color[2] + (bottom_color[2] - top_color[2]) * frac
            pygame.draw.line(self.surface, (int(r), int(g), int(b)), (0, y), (self.width, y))

        # Draw random cloud “blobs” as overlapping circles
        for _ in range(10):
            cx = random.randint(0, self.width)
            cy = random.randint(0, self.height // 2)
            max_r = random.randint(30, 60)
            for _ in range(5):
                r = random.randint(max_r // 2, max_r)
                offset_x = random.randint(-max_r // 2, max_r // 2)
                offset_y = random.randint(-max_r // 4, max_r // 4)
                alpha = random.randint(180, 240)
                cloud_surf = pygame.Surface((2*r, 2*r), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (255, 255, 255, alpha), (r, r), r)
                self.surface.blit(cloud_surf, (cx + offset_x - r, cy + offset_y - r))

    def _generate_black(self):
        """Fill the entire background with black."""
        self.surface.fill((0, 0, 0))

    def _generate_birthday_picnic(self):
        """Create a festive picnic scene with a cake, candles, balloons, plus
           random food and drinks scattered on the picnic cloth."""
        # 1) Sky (top half) and Grass (bottom half)
        sky_blue = (135, 206, 235)
        grass_green = (100, 180, 60)
        self.surface.fill(sky_blue)
        pygame.draw.rect(self.surface, grass_green, (0, self.height // 2, self.width, self.height // 2))

        # 2) Picnic blanket (checkered red/white) in bottom third
        blanket_w = int(self.width * 0.8)
        blanket_h = int(self.height * 0.2)
        blanket_x = (self.width - blanket_w) // 2
        blanket_y = int(self.height * 0.65)
        cell_size = 20
        for row in range(blanket_h // cell_size + 1):
            for col in range(blanket_w // cell_size + 1):
                x = blanket_x + col * cell_size
                y = blanket_y + row * cell_size
                color = (200, 50, 50) if (row + col) % 2 == 0 else (255, 255, 255)
                pygame.draw.rect(self.surface, color, (x, y, cell_size, cell_size))

        # Helper to pick a random position on the blanket
        def random_on_blanket(item_w, item_h):
            rx = random.randint(blanket_x, blanket_x + blanket_w - item_w)
            ry = random.randint(blanket_y, blanket_y + blanket_h - item_h)
            return rx, ry

        # 3) Cake with candles: center of the blanket
        cake_w = 100
        cake_h = 60
        cake_x = (self.width - cake_w) // 2
        cake_y = blanket_y - cake_h - 10
        # Cake base
        pygame.draw.rect(self.surface, (255, 200, 200), (cake_x, cake_y, cake_w, cake_h))
        # Frosting top layer
        frosting_h = 15
        pygame.draw.rect(self.surface, (255, 150, 200), (cake_x, cake_y, cake_w, frosting_h))
        # Candles on top of cake
        num_candles = random.randint(3, 7)
        candle_spacing = cake_w / (num_candles + 1)
        for i in range(num_candles):
            cx = cake_x + int((i + 1) * candle_spacing)
            cy = cake_y
            candle_h = 20
            candle_w = 6
            pygame.draw.rect(self.surface, (255, 255, 255), (cx - candle_w // 2, cy - candle_h, candle_w, candle_h))
            flame_center = (cx, cy - candle_h - 5)
            pygame.draw.circle(self.surface, (255, 200, 0), flame_center, 5)

        # 4) Balloons: random positions in top half
        balloon_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 200, 0), (255, 0, 255), (0, 255, 255)
        ]
        for _ in range(5):
            r = random.randint(15, 30)
            bx = random.randint(r, self.width - r)
            by = random.randint(r, self.height // 2 - r)
            color = random.choice(balloon_colors)
            pygame.draw.circle(self.surface, color, (bx, by), r)
            pygame.draw.ellipse(self.surface, (255, 255, 255, 100),
                                pygame.Rect(bx - r // 3, by - r // 2, r // 2, r // 3))
            pygame.draw.line(self.surface, (100, 100, 100), (bx, by + r),
                             (bx, by + r + 40), 2)

        # 5) Scatter confetti
        for _ in range(100):
            px = random.randint(0, self.width)
            py = random.randint(0, self.height)
            size = random.randint(2, 5)
            conf_color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            pygame.draw.rect(self.surface, conf_color, (px, py, size, size))

        # 6) Additional random food & drinks on the blanket
        #    a) Pizza slices (triangles with pepperoni)
        for _ in range(random.randint(2, 4)):
            slice_w = 30
            slice_h = 40
            px, py = random_on_blanket(slice_w, slice_h)
            # Triangle points (pointing up)
            p1 = (px + slice_w // 2, py)
            p2 = (px, py + slice_h)
            p3 = (px + slice_w, py + slice_h)
            pygame.draw.polygon(self.surface, (255, 230, 150), [p1, p2, p3])
            # Pepperoni circles
            for __ in range(3):
                rx = random.randint(px + 5, px + slice_w - 5)
                ry = random.randint(py + slice_h // 2, py + slice_h - 5)
                pygame.draw.circle(self.surface, (200, 50, 50), (rx, ry), 4)

        #    b) Sandwiches (rectangles with “filling” stripe)
        for _ in range(random.randint(2, 3)):
            sw = 40
            sh = 20
            px, py = random_on_blanket(sw, sh)
            # Bread top
            pygame.draw.rect(self.surface, (245, 222, 179), (px, py, sw, sh))
            # Filling stripe
            pygame.draw.rect(self.surface, (34, 139, 34), (px + 2, py + sh // 3, sw - 4, sh // 3))
            # Bread bottom
            pygame.draw.rect(self.surface, (245, 222, 179), (px, py + sh - 4, sw, 4))

        #    c) Fruit bowl (cluster of circles)
        for _ in range(random.randint(1, 2)):
            bowl_w = 40
            bowl_h = 25
            px, py = random_on_blanket(bowl_w, bowl_h)
            # Bowl base: a semi-circle
            pygame.draw.ellipse(self.surface, (222, 184, 135), (px, py, bowl_w, bowl_h))
            # Fruit inside as small circles
            for __ in range(6):
                fr = random.randint(4, 8)
                fx = random.randint(px + fr, px + bowl_w - fr)
                fy = random.randint(py + fr, py + bowl_h - fr)
                fcolor = random.choice([(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0)])
                pygame.draw.circle(self.surface, fcolor, (fx, fy), fr)

        #    d) Soda bottles (small rectangles with “label”)
        for _ in range(random.randint(2, 3)):
            bw = 10
            bh = 30
            px, py = random_on_blanket(bw, bh + 10)
            # Bottle body
            pygame.draw.rect(self.surface, (0, 100, 200), (px, py + 10, bw, bh))
            # Bottle neck
            pygame.draw.rect(self.surface, (0, 100, 200), (px + bw//4, py, bw//2, 10))
            # Label stripe
            pygame.draw.rect(self.surface, (255, 255, 255), (px + 1, py + 15, bw - 2, 6))

        #    e) Cups (circle + straw)
        for _ in range(random.randint(2, 4)):
            cw = 12
            ch = 16
            px, py = random_on_blanket(cw + 4, ch + 10)
            # Cup rim
            pygame.draw.ellipse(self.surface, (235, 235, 235), (px, py, cw, ch // 2))
            # Cup body
            pygame.draw.rect(self.surface, (235, 235, 235), (px + 1, py + ch // 4, cw - 2, ch // 2))
            # Straw (a thin line)
            straw_x = px + cw - 3
            straw_y1 = py
            straw_y2 = py - 8
            pygame.draw.line(self.surface, (255, 0, 0), (straw_x, straw_y1), (straw_x, straw_y2), 2)

        #    f) Cookies (small circles)
        for _ in range(random.randint(3, 5)):
            cr = random.randint(6, 10)
            px, py = random_on_blanket(cr * 2, cr * 2)
            pygame.draw.circle(self.surface, (210, 105, 30), (px + cr, py + cr), cr)
            # Chocolate chips as tiny darker dots
            for __ in range(5):
                chip_x = random.randint(px + 2, px + 2*cr - 2)
                chip_y = random.randint(py + 2, py + 2*cr - 2)
                pygame.draw.circle(self.surface, (101, 67, 33), (chip_x, chip_y), 2)

    def _generate_bathroom(self):
        """Draw a bathroom in profile with a larger sink and toilet."""
        # 1) Wall & floor
        wall_color  = (200, 225, 255)
        floor_color = (220, 220, 220)
        self.surface.fill(wall_color)
        floor_y = int(self.height * 0.6)
        pygame.draw.rect(self.surface, floor_color, (0, floor_y, self.width, self.height - floor_y))

        # 2) Backsplash tiles (top 60%)
        tile_size = 40
        grout = (180, 200, 230)
        for y in range(0, floor_y, tile_size):
            for x in range(0, self.width, tile_size):
                pygame.draw.rect(self.surface, grout, (x, y, tile_size, tile_size), 1)

        # 3) Big toilet on left (≈25% width, ≈60% height)
        toilet_w = int(self.width * 0.25)
        toilet_h = int((self.height - floor_y) * 0.6)
        tx = int(self.width * 0.05)
        ty = floor_y - toilet_h
        # Tank
        pygame.draw.rect(self.surface, (250, 250, 250),
                         (tx, ty, toilet_w, int(toilet_h * 0.35)))
        # Bowl (side‐view ellipse)
        bowl_rect = pygame.Rect(tx + toilet_w*0.1, ty + int(toilet_h*0.35),
                                 int(toilet_w*0.8), int(toilet_h*0.5))
        pygame.draw.ellipse(self.surface, (250, 250, 250), bowl_rect)
        # Seat (slightly inset)
        seat = bowl_rect.inflate(-int(toilet_w*0.15), -int(toilet_h*0.2))
        pygame.draw.ellipse(self.surface, (200, 200, 200), seat)
        # Foot (below the Bowl)
        pygame.draw.rect(self.surface, (250, 250, 250),
                         ((tx + toilet_w * 0.33), (ty + toilet_h * 0.85), int(toilet_w * 0.33), int(toilet_h * 0.35)))

        # 4) Big sink + mirror on right (≈30% width, ≈50% height)
        sink_w = int(self.width * 0.30)
        sink_h = int((self.height - floor_y) * 0.5)
        sx = int(self.width * 0.65)
        sy = floor_y - sink_h
        # Basin
        pygame.draw.rect(self.surface, (250, 250, 250),
                         (sx, sy, sink_w, sink_h))
        pygame.draw.ellipse(self.surface, (250, 250, 250),
                            (sx, sy + sink_h - int(sink_h*0.15), sink_w, int(sink_h*0.3)))
        # Faucet
        faucet_w = int(sink_w * 0.1)
        faucet_h = int(sink_h * 0.2)
        fx = sx + sink_w//2 - faucet_w//2
        fy = sy - faucet_h
        pygame.draw.rect(self.surface, (170,170,170), (fx, fy, faucet_w, faucet_h))
        pygame.draw.rect(self.surface, (170,170,170),
                         (fx - int(faucet_w*0.5), fy, int(faucet_w*2), int(faucet_h*0.3)))
        # Mirror (above sink)
        mirror_w = sink_w + 40
        mirror_h = int(sink_h * 0.8)
        mx = sx - 20
        my = sy - mirror_h - 20
        pygame.draw.rect(self.surface, (210,230,255),
                         (mx, my, mirror_w, mirror_h))
        pygame.draw.rect(self.surface, (180,200,230),
                         (mx + 5, my + 5, mirror_w - 10, mirror_h - 10), 2)

        # 5) Scattered toiletries on counter
        # Toothpaste tube
        for _ in range(2):
            tw, th = 20, 6
            px = random.randint(sx + 10, sx + sink_w - tw - 10)
            py = random.randint(sy + 10, sy + sink_h - th - 10)
            pygame.draw.rect(self.surface, (255,255,255), (px, py, tw, th))
            pygame.draw.rect(self.surface, random.choice([(255,0,0),(0,100,200),(0,200,0)]),
                             (px+2, py+1, tw-4, th-2))
        # Soap bar
        sb_w, sb_h = 24, 12
        px = random.randint(sx + 10, sx + sink_w - sb_w - 10)
        py = random.randint(sy + 10, sy + sink_h - sb_h - 10)
        pygame.draw.rect(self.surface, (255,200,200), (px, py, sb_w, sb_h))
        # Hand towel
        tw_w, tw_h = 40, 16
        tx2 = mx + 10
        ty2 = my + mirror_h + 10
        pygame.draw.rect(self.surface, random.choice([(200,200,200),(200,180,180),
                                                      (180,200,180)]),
                         (tx2, ty2, tw_w, tw_h))
        pygame.draw.line(self.surface, (150,150,150),
                         (tx2, ty2), (tx2 + tw_w, ty2), 3)


    def _generate_wild_flowers(self):
        """Wild flower meadow with dirt strip, profile flowers, bees, etc."""
        # 1) Sky gradient
        sky_top = (135, 206, 235)
        sky_bot = (200, 230, 255)
        for y in range(self.height):
            t = y / self.height
            r = sky_top[0] + (sky_bot[0] - sky_top[0]) * t
            g = sky_top[1] + (sky_bot[1] - sky_top[1]) * t
            b = sky_top[2] + (sky_bot[2] - sky_top[2]) * t
            pygame.draw.line(self.surface, (int(r), int(g), int(b)), (0, y), (self.width, y))

        # 2) Sun in top-right
        sun_r = 40
        sun_pos = (int(self.width * 0.85), int(self.height * 0.15))
        pygame.draw.circle(self.surface, (255, 255, 100), sun_pos, sun_r)

        # 3) Dirt strip along bottom
        dirt_h = int(self.height * 0.15)
        dirt_color = (101, 67, 33)
        pygame.draw.rect(self.surface, dirt_color,
                         (0, self.height - dirt_h, self.width, dirt_h))
        base_y = self.height - dirt_h

        # 4) Grass tufts on edge of dirt
        grass_color = (80, 160, 40)
        for x in range(0, self.width, 12):
            tuft_h = random.randint(15, 30)
            pygame.draw.line(self.surface, grass_color, (x, base_y), (x, base_y - tuft_h), 2)

        # 5) Profile flowers
        for _ in range(random.randint(12, 18)):
            fx = random.randint(20, self.width - 20)
            stem_h = random.randint(50, 120)
            top_x, top_y = fx, base_y - stem_h

            # stem
            pygame.draw.line(self.surface, (34, 139, 34),
                             (fx, base_y), (top_x, top_y), 3)

            # leaves (two per stem)
            for _ in range(2):
                ly = base_y - random.randint(stem_h//3, stem_h*2//3)
                lx = fx + random.choice([-1, 1]) * random.randint(8, 12)
                pygame.draw.ellipse(self.surface, (34, 139, 34),
                                    (lx, ly, 12, 6))

            # petals around top point
            petals = random.randint(5, 8)
            petal_r = random.randint(8, 12)
            petal_col = (
                random.randint(200, 255),
                random.randint(100, 200),
                random.randint(100, 200)
            )
            for i in range(petals):
                angle = 2*math.pi * i / petals
                px = top_x + math.cos(angle) * petal_r
                py = top_y + math.sin(angle) * petal_r
                pygame.draw.circle(self.surface, petal_col,
                                   (int(px), int(py)), petal_r//2)

            # central stamen
            pygame.draw.circle(self.surface, (200, 200, 50),
                               (top_x, top_y), petal_r//3)

        # 6) Bees buzzing around
        for _ in range(5):
            bx = random.randint(20, self.width - 20)
            by = random.randint(20, base_y - 40)
            br = 5
            # body
            pygame.draw.circle(self.surface, (255, 200, 0), (bx, by), br)
            # stripe
            pygame.draw.line(self.surface, (0, 0, 0),
                             (bx - br, by), (bx + br, by), 2)
            # wings
            pygame.draw.ellipse(self.surface, (255, 255, 255),
                                (bx - 8, by - 6, 6, 4))
            pygame.draw.ellipse(self.surface, (255, 255, 255),
                                (bx + 2, by - 6, 6, 4))

    def _generate_kitchen_counter(self):
        """Top-down kitchen counter segment with board, knife, crumbs, veggies, utensils."""
        # 1) Wood-grain countertop base
        counter_color = (140, 100, 60)
        self.surface.fill(counter_color)
        # Simple horizontal “grain” lines
        for y in range(0, self.height, 12):
            shade = random.randint(-10, 10)
            line_color = (
                max(0, min(255, counter_color[0] + shade)),
                max(0, min(255, counter_color[1] + shade)),
                max(0, min(255, counter_color[2] + shade))
            )
            pygame.draw.line(self.surface, line_color, (0, y), (self.width, y), 2)

        # 2) Cutting board (centered)
        board_w = int(self.width * 0.6)
        board_h = int(self.height * 0.4)
        bx = (self.width - board_w) // 2
        by = (self.height - board_h) // 2
        board_color = (200, 180, 140)
        pygame.draw.rect(self.surface, board_color, (bx, by, board_w, board_h))
        pygame.draw.rect(self.surface, (160, 140, 100), (bx, by, board_w, board_h), 4)

        # 3) Knife (top-down) on board
        k_w, k_h = int(board_w * 0.7), 8
        kx = bx + board_w // 4
        ky = by + board_h // 3
        # blade
        pygame.draw.rect(self.surface, (230, 230, 230), (kx, ky, k_w, k_h))
        # handle
        pygame.draw.rect(self.surface, (50, 50, 50), (kx + k_w - 12, ky - 2, 12, k_h + 4))

        # 4) Crumbs scattered
        for _ in range(40):
            cx = random.randint(bx - 20, bx + board_w + 20)
            cy = random.randint(by - 20, by + board_h + 20)
            pygame.draw.circle(self.surface, (150, 100, 50), (cx, cy), 2)

        # 5) Veggie slices on board
        #   a) Carrot rounds (orange)
        for _ in range(6):
            r = random.randint(5, 8)
            vx = random.randint(bx + 10, bx + board_w - 10)
            vy = random.randint(by + 10, by + board_h - 10)
            pygame.draw.circle(self.surface, (255, 165, 0), (vx, vy), r)
        #   b) Cucumber slices (green rings)
        for _ in range(5):
            w = random.randint(12, 18)
            h = random.randint(6, 10)
            vx = random.randint(bx + 10, bx + board_w - w - 10)
            vy = random.randint(by + 10, by + board_h - h - 10)
            pygame.draw.ellipse(self.surface, (144, 238, 144), (vx, vy, w, h))
            pygame.draw.ellipse(self.surface, (34, 139, 34), (vx+2, vy+2, w-4, h-4), 1)
        #   c) Tomato slices (red circles)
        for _ in range(4):
            r = random.randint(6, 10)
            vx = random.randint(bx + 10, bx + board_w - 10)
            vy = random.randint(by + 10, by + board_h - 10)
            pygame.draw.circle(self.surface, (255, 0, 0), (vx, vy), r)
            pygame.draw.circle(self.surface, (180, 0, 0), (vx, vy), r//2)
        #   d) Onion rings (white circles)
        for _ in range(3):
            r = random.randint(8, 12)
            vx = random.randint(bx + 10, bx + board_w - 10)
            vy = random.randint(by + 10, by + board_h - 10)
            pygame.draw.circle(self.surface, (255, 255, 255), (vx, vy), r, 2)

        # 6) Occasional salad bowl
        if random.random() < 0.5:
            bowl_r = board_w // 6
            bx2 = random.randint(bx + board_w//2 - bowl_r, bx + board_w//2 + bowl_r)
            by2 = random.randint(by + board_h//2 - bowl_r, by + board_h//2 + bowl_r)
            pygame.draw.circle(self.surface, (200, 200, 200), (bx2, by2), bowl_r)
            # lettuce “leaves”
            for _ in range(10):
                lr = random.randint(3, 6)
                lx = random.randint(bx2 - bowl_r + lr, bx2 + bowl_r - lr)
                ly = random.randint(by2 - bowl_r + lr, by2 + bowl_r - lr)
                pygame.draw.circle(self.surface, (34, 139, 34), (lx, ly), lr)

        # 7) Utensils on countertop
        for _ in range(2):
            uw = 4
            uh = random.randint(30, 50)
            ux = random.randint(10, self.width - uw - 10)
            uy = random.randint(self.height - uh - 10, self.height - uh - 5)
            pygame.draw.rect(self.surface, (200, 200, 200), (ux, uy, uw, uh))

        # 8) Spice jars / condiments near edge
        for _ in range(2):
            cw = 12
            ch = 24
            cx2 = random.choice([bx - cw - 20, bx + board_w + 20])
            cy2 = random.randint(by + board_h//4, by + board_h - ch)
            color = random.choice([(180, 50, 50), (50, 50, 180), (180, 180, 50)])
            pygame.draw.rect(self.surface, color, (cx2, cy2, cw, ch))
            pygame.draw.rect(self.surface, (100, 100, 100), (cx2, cy2, cw, 4))  # lid

    def draw(self, target_surface):
        target_surface.blit(self.surface, (0, 0))


class Insect:
    """
    Represents a single 8-bit–style insect with optional wings, tail/stinger, fangs, eyes,
    stripes/spots/plain patterns, proboscis or horns, plus movement and dancing legs/antennae.
    """
    GRID_W = 16
    GRID_H = 16

    def __init__(self, screen_width, screen_height, pixel_size):
        # 1) Build a random 3-color palette for body/base, shade, and accent
        base_r = random.randint(50, 200)
        base_g = random.randint(50, 200)
        base_b = random.randint(50, 200)
        self.body_color   = (base_r, base_g, base_b)
        self.shade_color  = (max(base_r - 50, 0), max(base_g - 50, 0), max(base_b - 50, 0))
        self.accent_color = (min(base_r + 50, 255), min(base_g + 50, 255), min(base_b + 50, 255))

        # 2) Variety of eye colors
        eye_color_choices = [
            (255, 255, 255),  # white
            (255, 255, 0),    # yellow
            (0, 255, 255),    # cyan
            (255, 0, 255),    # magenta
            (255, 128, 0),    # orange
            (0, 255, 0)       # bright green
        ]
        self.eye_color    = random.choice(eye_color_choices)

        self.palette = {
            1: self.body_color,   # body/head
            2: self.shade_color,  # legs/tail/spots
            3: self.accent_color, # antennae/fangs/wings/horns/proboscis
            4: self.eye_color     # eyes
        }

        # 3) Choose random body/head sizes (odd numbers for symmetry)
        self.body_w_px = random.choice([5, 7])   # must be odd
        self.body_h_px = random.choice([5, 7, 9])       # must be odd
        self.head_w_px = random.choice([5, 7, 9])
        self.head_h_px = random.choice([3, 4, 5])

        # 4) Center coordinates in grid
        self.cx = Insect.GRID_W // 2      # 8
        self.cy = Insect.GRID_H // 2 + 1  # 9 (shifted down for antennae)

        # 5) Precompute leg attach points (3 on right side)
        self.num_legs = 3
        self.leg_attach = []
        for i in range(self.num_legs):
            ay = self.cy - (self.body_h_px // 2) + int((i + 1) * (self.body_h_px / (self.num_legs + 1)))
            ax = self.cx + (self.body_w_px // 2)
            self.leg_attach.append((ax, ay))

        # 6) Pick base angles + phases for legs
        self.leg_base_angles = [random.uniform(-45, 45) for _ in range(self.num_legs)]
        self.leg_wiggle_amp = 15  # degrees
        self.leg_phases = [random.uniform(0, 2 * math.pi) for _ in range(self.num_legs)]

        # 7) Compute antenna attach point + base angle/phase
        head_cx = self.cx
        head_cy = self.cy - (self.body_h_px // 2) - (self.head_h_px // 2)
        head_top_y = head_cy - (self.head_h_px // 2)
        offset_x = self.head_w_px // 4
        self.ant_attach = (head_cx + offset_x, head_top_y + 1)
        self.ant_base_angle = random.uniform(-70, -20)
        self.ant_wiggle_amp = 15
        self.ant_phase = random.uniform(0, 2 * math.pi)

        # 8) Random pattern: plain, stripes, or spots
        self.pattern = random.choice(["plain", "stripes", "spots"])

        # 9) Randomly decide additional features
        self.has_wings    = random.random() < 0.5
        self.has_tail     = random.random() < 0.5
        self.has_fangs    = random.random() < 0.5
        self.has_eyes     = True  # Always draw eyes
        self.has_proboscis = random.random() < 0.3
        self.has_horns    = (not self.has_proboscis) and (random.random() < 0.3)

        # 10) Initialize screen bounds and pixel size for movement
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.pixel_size = pixel_size
        sprite_w = Insect.GRID_W * pixel_size
        sprite_h = Insect.GRID_H * pixel_size

        # 11) Set initial random position within bounds
        self.x = random.uniform(0, self.screen_w - sprite_w)
        self.y = random.uniform(0, self.screen_h - sprite_h)

        # 12) Assign a random base velocity and jitter speed
        speed = random.uniform(30, 240)  # pixels per second
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.jitter_amount = 20  # max jitter in pixels per second

        # 13) Calculate sprite dimensions for bounds checking
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h

    def update(self, dt):
        """
        Update insect position with base velocity and jitter, bouncing off edges.
        dt: time elapsed (in seconds) since last frame.
        """
        jitter_vx = random.uniform(-self.jitter_amount, self.jitter_amount)
        jitter_vy = random.uniform(-self.jitter_amount, self.jitter_amount)
        dx = (self.vx + jitter_vx) * dt
        dy = (self.vy + jitter_vy) * dt

        new_x = self.x + dx
        new_y = self.y + dy

        if new_x < 0:
            new_x = -new_x
            self.vx = -self.vx
        elif new_x + self.sprite_w > self.screen_w:
            new_x = 2 * (self.screen_w - self.sprite_w) - new_x
            self.vx = -self.vx

        if new_y < 0:
            new_y = -new_y
            self.vy = -self.vy
        elif new_y + self.sprite_h > self.screen_h:
            new_y = 2 * (self.screen_h - self.sprite_h) - new_y
            self.vy = -self.vy

        self.x = new_x
        self.y = new_y

    def render(self, t):
        """
        Renders the insect’s current pose (with dancing legs/antennae,
        optional features, pattern, and additional horns/proboscis) into a Surface.
        - `t` is time in seconds for animating legs/antennae.
        """
        pixel_size = self.pixel_size
        # 1) Blank 16×16 grid (0 = transparent)
        sprite = [[0 for _ in range(Insect.GRID_W)] for _ in range(Insect.GRID_H)]

        # 2) Draw body (static ellipse, index = 1)
        for y in range(Insect.GRID_H):
            for x in range(Insect.GRID_W):
                dx = (x - self.cx) / (self.body_w_px / 2)
                dy = (y - self.cy) / (self.body_h_px / 2)
                if dx*dx + dy*dy <= 1.0:
                    sprite[y][x] = 1

        # 3) Apply pattern: stripes or spots
        if self.pattern == "stripes":
            # Vertical stripes within body ellipse
            for y in range(Insect.GRID_H):
                for x in range(Insect.GRID_W):
                    if sprite[y][x] == 1 and (x - self.cx) % 2 == 0:
                        sprite[y][x] = 2  # use shade color for stripe
        elif self.pattern == "spots":
            # Checkerboard pattern: shade every other pixel within the body ellipse
            for y in range(Insect.GRID_H):
                for x in range(Insect.GRID_W):
                    dx = (x - self.cx) / (self.body_w_px / 2)
                    dy = (y - self.cy) / (self.body_h_px / 2)
                    if dx*dx + dy*dy <= 1.0:
                        if (x + y) % 2 == 0:
                            sprite[y][x] = 2  # shade color for spot

        # 4) Draw head (static smaller ellipse, index = 1)
        head_cx = self.cx
        head_cy = self.cy - (self.body_h_px // 2) - (self.head_h_px // 2)
        for y in range(Insect.GRID_H):
            for x in range(Insect.GRID_W):
                dx = (x - head_cx) / (self.head_w_px / 2)
                dy = (y - head_cy) / (self.head_h_px / 2)
                if dx*dx + dy*dy <= 1.0:
                    sprite[y][x] = 1

        # 5) Draw eyes (index = 4) on head
        if self.has_eyes:
            eye_y = head_cy
            left_eye_x  = head_cx - 2
            right_eye_x = head_cx + 2
            if 0 <= eye_y < Insect.GRID_H:
                if 0 <= left_eye_x < Insect.GRID_W:
                    sprite[eye_y][left_eye_x] = 4
                if 0 <= right_eye_x < Insect.GRID_W:
                    sprite[eye_y][right_eye_x] = 4

        # 6) Draw larger wings (index = 3), symmetric on both sides
        if self.has_wings:
            wing_color_idx = 3
            # make wings two pixels out from body over three rows
            for dy_off in (-1, 0, 1):
                y_pos = self.cy + dy_off
                for dx_off in (-(self.body_w_px//2 + 2), self.body_w_px//2 + 2):
                    for w_dx in (0, 1):  # wing thickness of 2 pixels
                        x_w = self.cx + dx_off + (w_dx if dx_off > 0 else -w_dx)
                        if 0 <= x_w < Insect.GRID_W and 0 <= y_pos < Insect.GRID_H:
                            sprite[y_pos][x_w] = wing_color_idx

        # 7) Draw tail/stinger (index = 2)
        if self.has_tail:
            tail_color_idx = 2
            for i in (1, 2):
                y_tail = self.cy + (self.body_h_px // 2) + i
                x_tail = self.cx
                if 0 <= x_tail < Insect.GRID_W and 0 <= y_tail < Insect.GRID_H:
                    sprite[y_tail][x_tail] = tail_color_idx

        # 8) Draw fangs (index = 3)
        if self.has_fangs:
            fang_color_idx = 3
            fang_y = head_cy - (self.head_h_px // 2) - 1
            for dx_f in (-1, 1):
                fang_x = head_cx + dx_f
                if 0 <= fang_x < Insect.GRID_W and 0 <= fang_y < Insect.GRID_H:
                    sprite[fang_y][fang_x] = fang_color_idx

        # 9) Draw proboscis (index = 3): a small tube extending from head center downwards
        if self.has_proboscis:
            prob_color_idx = 3
            p_x = head_cx
            p_y_start = head_cy + (self.head_h_px // 2)
            for i in range(3):
                py = p_y_start + i
                if 0 <= p_x < Insect.GRID_W and 0 <= py < Insect.GRID_H:
                    sprite[py][p_x] = prob_color_idx

        # 10) Draw horns (index = 3): two small pixels above head
        if self.has_horns:
            horn_color_idx = 3
            horn_y = head_cy - (self.head_h_px // 2) - 1
            for dx_h in (-2, 2):
                hx = head_cx + dx_h
                if 0 <= hx < Insect.GRID_W and 0 <= horn_y < Insect.GRID_H:
                    sprite[horn_y][hx] = horn_color_idx

        # 11) Animate right-side legs (index = 2)
        for i, (ax, ay) in enumerate(self.leg_attach):
            angle = self.leg_base_angles[i] + self.leg_wiggle_amp * math.sin(3 * t + self.leg_phases[i])
            angle_rad = math.radians(angle)
            leg_length = random.randint(3, 5)
            for step in range(leg_length):
                fx = ax + math.cos(angle_rad) * step
                fy = ay + math.sin(angle_rad) * step
                ix = int(round(fx))
                iy = int(round(fy))
                if 0 <= ix < Insect.GRID_W and 0 <= iy < Insect.GRID_H:
                    sprite[iy][ix] = 2

        # 12) Animate right-side antenna (index = 3)
        ant_x, ant_y = self.ant_attach
        ant_angle = self.ant_base_angle + self.ant_wiggle_amp * math.sin(3 * t + self.ant_phase)
        ant_rad = math.radians(ant_angle)
        ant_length = random.randint(3, 5)
        for step in range(ant_length):
            fx = ant_x + math.cos(ant_rad) * step
            fy = ant_y + math.sin(ant_rad) * step
            ix = int(round(fx))
            iy = int(round(fy))
            if 0 <= ix < Insect.GRID_W and 0 <= iy < Insect.GRID_H:
                sprite[iy][ix] = 3

        # 13) Mirror non-zero pixels across the vertical axis for symmetry
        for y in range(Insect.GRID_H):
            for x in range(Insect.GRID_W):
                idx = sprite[y][x]
                if idx != 0:
                    mx = (Insect.GRID_W - 1) - x
                    sprite[y][mx] = idx

        # 14) Render the 16×16 grid into a Surface, scaled by pixel_size
        spr_w = Insect.GRID_W * pixel_size
        spr_h = Insect.GRID_H * pixel_size
        temp = pygame.Surface((spr_w, spr_h), pygame.SRCALPHA)
        temp.fill((0, 0, 0, 0))

        for y in range(Insect.GRID_H):
            for x in range(Insect.GRID_W):
                idx = sprite[y][x]
                if idx != 0:
                    color = self.palette[idx]
                    rect = pygame.Rect(x * pixel_size, y * pixel_size, pixel_size, pixel_size)
                    pygame.draw.rect(temp, color, rect)

        # 15) (Optional) shiny highlight for special gold bug
        # ───────────────────────────────────────────────────────────────
        if getattr(self, "is_special", False):
            # 'temp' (or 'surf') is the final Surface holding the pixels.
            w, h = temp.get_size()   # same size as the scaled sprite
            # Create a small transparent surface for the glint
            glint = pygame.Surface((w // 3, h // 3), pygame.SRCALPHA)
            # Draw a soft white ellipse (alpha 120 ≈ 47%)
            pygame.draw.ellipse(glint, (255, 255, 255, 120), glint.get_rect())
            # Blit it near the upper-left quadrant for a specular highlight
            temp.blit(glint, (w // 8, h // 8))
            # You can move the (w//8, h//8) offset to taste.

        # ───────────────────────────────────────────────────────────────

        return temp


     # ───────────────────────────────── save / load ─────────────────────────
    def to_dict(self):
        """Return a JSON-serializable snapshot of this insect."""
        return {
            "x": self.x, "y": self.y,
            "pixel_size": self.pixel_size,
            "body_color":   self.body_color,
            "shade_color":  self.shade_color,
            "accent_color": self.accent_color,
            "eye_color":    self.eye_color,
            "pattern":  self.pattern,
            "has_wings": self.has_wings,
            "has_tail":  self.has_tail,
            "has_fangs": self.has_fangs,
            "has_proboscis": self.has_proboscis,
            "has_horns": self.has_horns,
            "vx": self.vx, "vy": self.vy,
            "is_special": getattr(self, "is_special", False),
            "spin_speed": getattr(self, "spin_speed", 0),
            "spawn_time": getattr(self, "spawn_time", 0),
        }

    @staticmethod
    def from_dict(d, screen_w, screen_h):
        """Re-create an Insect from its dictionary snapshot."""
        bug = Insect(screen_w, screen_h, d["pixel_size"])
        bug.x, bug.y = d["x"], d["y"]
        bug.body_color, bug.shade_color = tuple(d["body_color"]), tuple(d["shade_color"])
        bug.accent_color, bug.eye_color = tuple(d["accent_color"]), tuple(d["eye_color"])
        bug.pattern = d["pattern"]
        bug.has_wings = d["has_wings"]
        bug.has_tail  = d["has_tail"]
        bug.has_fangs = d["has_fangs"]
        bug.has_proboscis = d["has_proboscis"]
        bug.has_horns = d["has_horns"]
        bug.vx, bug.vy = d["vx"], d["vy"]
        bug.is_special = d["is_special"]
        if bug.is_special:
            bug.spin_speed = d["spin_speed"]
            bug.spawn_time = d["spawn_time"]
        # rebuild palette with custom colors
        bug.palette = {1: bug.body_color, 2: bug.shade_color,
                       3: bug.accent_color, 4: bug.eye_color}
        return bug

class Particle:
    """
    Represents a single particle for the burst effect.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # random velocity
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(50, 150)  # px/sec
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        # random color
        self.color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255)
        )
        self.life = random.uniform(0.5, 1.0)  # seconds
        self.age = 0
        self.size = random.randint(4, 10)  # initial size

    def update(self, dt):
        self.age += dt
        # move
        self.x += self.vx * dt
        self.y += self.vy * dt
        # fade out by shrinking
        self.size = max(0, self.size * (1 - dt / self.life))

    def draw(self, surface):
        if self.age < self.life and self.size > 0:
            alpha = int(255 * (1 - self.age / self.life))
            surf = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            surf.fill((*self.color, alpha))
            surface.blit(surf, (self.x, self.y))

def create_window(width, height, title):
    """
    Initialize Pygame, including audio mixer, and create a resizable window.
    """
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(title)
    return screen

pygame.mixer.init()

# Get the mixer’s sample rate / format:
mixer_freq, mixer_fmt, mixer_channels = pygame.mixer.get_init()
# mixer_freq is typically 44100 or 48000, etc.

# Load the WAV file into a Sound and then grab its array
try:
    orig_pop_sound = pygame.mixer.Sound("pop.wav")
    # Convert it into a NumPy array (shape: [n_samples, channels])
    orig_sound_array = pygame.sndarray.array(orig_pop_sound)
    orig_num_samples = orig_sound_array.shape[0]
    # Determine if mono or stereo
    if orig_sound_array.ndim == 1:
        orig_num_channels = 1
    else:
        orig_num_channels = orig_sound_array.shape[1]
except Exception:
    orig_pop_sound = None
    orig_sound_array = None
    orig_num_samples = 0
    orig_num_channels = 1

# Choose a “reference” bug‐pixel_size that corresponds to original pitch.
# In our code, the base pixel_size was 5.
REF_PIXEL_SIZE = 5


def make_pitch_shifted_sound(bug_pixel_size: int) -> pygame.mixer.Sound:
    """
    Returns a new Sound object whose pitch is shifted according to bug_pixel_size.
    Smaller bug_pixel_size ⇒ higher pitch ⇒ playback speed up;
    larger bug_pixel_size ⇒ lower pitch ⇒ playback speed down.
    """
    if orig_sound_array is None:
        return None

    # 2) Compute pitch ratio:   original should correspond to REF_PIXEL_SIZE
    ratio = REF_PIXEL_SIZE / float(bug_pixel_size)
    # If bug_pixel_size < REF_PIXEL_SIZE, ratio > 1 ⇒ pitch ↑. If bug_pixel_size > REF_PIXEL_SIZE, ratio <1 ⇒ pitch ↓.

    # 3) Calculate new number of samples: 
    new_num_samples = max(1, int(orig_num_samples / ratio))

    # 4) Build a new resampled array (Nc = orig_num_channels)
    #    We will linearly interpolate each channel independently.
    if orig_num_channels == 1:
        # Mono: orig_sound_array is shape (orig_num_samples,)
        old_indices = np.linspace(0, orig_num_samples - 1, num=orig_num_samples)
        new_indices = np.linspace(0, orig_num_samples - 1, num=new_num_samples)
        new_array = np.interp(new_indices, old_indices, orig_sound_array).astype(orig_sound_array.dtype)
        # Reshape back to 1D
    else:
        # Stereo (or more channels):
        new_array = np.zeros((new_num_samples, orig_num_channels), dtype=orig_sound_array.dtype)
        old_indices = np.linspace(0, orig_num_samples - 1, num=orig_num_samples)
        new_indices = np.linspace(0, orig_num_samples - 1, num=new_num_samples)
        for ch in range(orig_num_channels):
            new_array[:, ch] = np.interp(
                new_indices,
                old_indices,
                orig_sound_array[:, ch]
            ).astype(orig_sound_array.dtype)

    # 5) Create a new Sound from the resampled array and return it
    new_sound = pygame.sndarray.make_sound(new_array)
    return new_sound

def draw_center_text(surface, text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect.topleft)
    return rect     # we’ll use this for click detection

def main():
    width, height = 800, 600
    pixel_size = REF_PIXEL_SIZE

    screen = create_window(width, height, "SUPER SKITTER BUGS")
    clock = pygame.time.Clock()

    # Fonts for menu, score & popups
    title_font = pygame.font.SysFont(None, 80, italic=True)
    menu_font  = pygame.font.SysFont(None, 48)
    font = pygame.font.SysFont(None, 36)

    # ── game state ────────────────────────
    state = GameState.MENU
    
    # Helper to create a fresh batch of insects
    def new_batch():
        num = random.randint(1, 12)
        return [Insect(width, height, pixel_size + random.randint(-3, 3)) for _ in range(num)]

    # Create a procedurally generated background
    # List of all styles, in the order you want to cycle
    styles = Background.STYLES
    current_style_idx = 0

    # ── variables that only matter in PLAY state (unchanged) ──
    #  (put your existing setup here: insects list, score, bg, etc.)
    def start_new_game():
        nonlocal insects, score, bg, particles, popups, special_bug, level, MAX_INSECTS
        score      = 0
        insects    = new_batch()      # call your existing new_batch()
        bg         = Background(width, height, style=styles[current_style_idx])
        particles  = []
        popups     = []
        special_bug = None
        level = 1
        MAX_INSECTS = level


    def save_game():
        data = {
            "level": level,
            "score": score,
            "style_idx": current_style_idx,
            "insects": [ins.to_dict() for ins in insects],
            "special": special_bug.to_dict() if special_bug else None
        }
        with open(SAVEFILE, "w") as f:
            json.dump(data, f)
        print("Game saved.")

    def load_game():
        nonlocal insects, score, bg, particles, popups, special_bug, level, MAX_INSECTS, current_style_idx
        if not os.path.exists(SAVEFILE):
            start_new_game()
            return
        with open(SAVEFILE, "r") as f:
            data = json.load(f)
        level  = data.get("level", 1)
        score  = data.get("score", 0)
        current_style_idx = data.get("style_idx", 0) % len(styles)
        bg = Background(width, height, style=styles[current_style_idx])

        insects = [Insect.from_dict(d, width, height) for d in data.get("insects", [])]
        sdict = data.get("special")
        special_bug = Insect.from_dict(sdict, width, height) if sdict else None

        particles, popups = [], []
        MAX_INSECTS = level
        print("Game loaded.")

    # Special gold bug settings
    SPECIAL_MIN_INTERVAL = 10_000       # at least 10s between spawns
    SPECIAL_MAX_INTERVAL = 20_000       # at most 20s between spawns
    SPECIAL_LIFESPAN      = 5_000       # lives 5 seconds if not clicked
    SPECIAL_PARTICLES     = 200         # big burst on click
    SPECIAL_MULTIPLIER    = 20          # 20× points

    # Prepare popup list (each popup is a dict with its own data)
    popups = []
    POP_DURATION = 1000  # milliseconds
    FLOAT_PIXELS = 30    # pixels to float upward

    # Particle list
    particles = []

    # Respawn effect state
    respawning = False
    respawn_start = 0
    RESPAWN_DURATION = 0.5  # seconds

    #Initialize the gold bugs
    special_bug = None
    special_spawn_time = 0
    next_special_spawn = pygame.time.get_ticks() + random.randint(
        SPECIAL_MIN_INTERVAL, SPECIAL_MAX_INTERVAL
    )


    running = True
    while running:
        dt = clock.tick(60) / 1000.0        # seconds elapsed since last frame
        now_ms = pygame.time.get_ticks()    # current time in ms
        t = now_ms / 1000.0                 # time in seconds for animation

        # --- handle special-bug spawn / timeout ---
        if special_bug is None:
            # time to spawn?
            if now_ms >= next_special_spawn:
                # spawn at random location
                px = random.randint(0, width - Insect.GRID_W*pixel_size)
                py = random.randint(0, height - Insect.GRID_H*pixel_size)
                special_bug = Insect(width, height, pixel_size)
                special_bug.x = px
                special_bug.y = py
                special_bug.is_special = True
                special_bug.spawn_time = now_ms
                special_bug.spin_speed = random.uniform(180, 360)  # deg/sec
                # Override its colors to rich gold tones:
                special_bug.body_color   = (212, 175,  55)   # gold
                special_bug.shade_color  = (184, 134,  11)   # darker gold
                special_bug.accent_color = (255, 223,   0)   # bright highlight
                special_bug.eye_color    = (255, 255, 255)   # white eyes

                # Rebuild its palette dict:
                special_bug.palette = {
                    1: special_bug.body_color,
                    2: special_bug.shade_color,
                    3: special_bug.accent_color,
                    4: special_bug.eye_color
                }
        else:
            # timeout?
            if now_ms - special_bug.spawn_time > SPECIAL_LIFESPAN:
                special_bug = None
                next_special_spawn = now_ms + random.randint(
                    SPECIAL_MIN_INTERVAL, SPECIAL_MAX_INTERVAL
                )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ───────────────── MENU EVENTS ────────────────
            if state == GameState.MENU and event.type == pygame.MOUSEBUTTONDOWN \
               and event.button == 1:
                mx, my = event.pos
                if new_rect.collidepoint(mx, my):
                    start_new_game()
                    state = GameState.PLAY
                elif cont_rect.collidepoint(mx, my):
                    load_game()      # loads
                    state = GameState.PLAY
            
            # ───────────────── PLAY EVENTS ────────────────
            if state == GameState.PLAY:

                if event.type == pygame.VIDEORESIZE:
                    width, height = event.w, event.h
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                    bg = Background(width, height)  # regenerate background for new size
                    # Inform each insect of new bounds
                    for insect in insects:
                        insect.screen_w = width
                        insect.screen_h = height

                #Push 'c' to cycle through the backgrounds
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    # advance to next style, wrap around
                    current_style_idx = (current_style_idx + 1) % len(styles)
                    bg = Background(width, height, style=styles[current_style_idx])

                #Push 'r' to redraw the background
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    bg = Background(width, height, style=styles[current_style_idx])

                 #Save game
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s and state == GameState.PLAY:
                    save_game()

                # Quit on ESC (no auto-save)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                
                #Mouse button click handler
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    to_remove = None
                    # first check special bug
                    if special_bug:
                        rect = pygame.Rect(int(special_bug.x), int(special_bug.y),
                                           special_bug.sprite_w, special_bug.sprite_h)
                        if rect.collidepoint(mx, my):
                            # 20× points
                            pts = random.randint(10, 100) * SPECIAL_MULTIPLIER
                            score += pts
                            #play the pop sound effect
                            orig_pop_sound.play()
                            # big particle burst
                            for _ in range(SPECIAL_PARTICLES):
                                particles.append(Particle(mx, my))
                            # popup as usual
                            popups.append({
                                "surf": font.render(f"+{pts}", True, (255,255,0)).convert_alpha(),
                                "x": mx, "y": my, "start": now_ms
                            })
                            # remove special
                            special_bug = None
                            next_special_spawn = now_ms + random.randint(
                                SPECIAL_MIN_INTERVAL, SPECIAL_MAX_INTERVAL
                            )
                            # skip ordinary click handling
                            continue
                    for idx, insect in enumerate(insects):
                        rect = pygame.Rect(int(insect.x), int(insect.y),
                                           insect.sprite_w, insect.sprite_h)
                        if rect.collidepoint(mx, my):
                            to_remove = idx
                            break
                    if to_remove is not None:
                        # Calculate points & increment score
                        points = random.randint(10, 100)
                        score += points

                        # Play click sound
                        shifted_sound = make_pitch_shifted_sound(insects[to_remove].pixel_size)
                        if shifted_sound:
                            shifted_sound.play()

                        # Create popup at insect's top-center
                        insect = insects[to_remove]
                        px = int(insect.x) + insect.sprite_w // 2
                        py = int(insect.y)
                        surf = font.render(f"+{points}", True, (255, 255, 255)).convert_alpha()
                        popups.append({"surf": surf, "x": px, "y": py, "start": now_ms})

                        # Generate particle burst at click location
                        for _ in range(20):
                            particles.append(Particle(mx, my))

                        # Remove the clicked insect
                        insects.pop(to_remove)

                        # If none remain, spawn a new batch
                        if not insects:
                            respawning = True
                            respawn_start = now_ms


        # ───────────────── DRAW ───────────────────────────
        if state == GameState.MENU:
            screen.fill((30, 30, 40))

            # title & buttons
            draw_center_text(screen, "SUPER SKITTER BUGS", title_font,
                             (255, 215, 0), height//3)
            new_rect  = draw_center_text(screen, "New Game",  menu_font,
                                         (200, 255, 200), height//3 + 100)
            cont_rect = draw_center_text(screen, "Continue Game", menu_font,
                                         (200, 200, 255), height//3 + 170)

            # subtle hover effect
            mx, my = pygame.mouse.get_pos()
            if new_rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255,255,255), new_rect, 2)
            if cont_rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255,255,255), cont_rect, 2)

        else:   # state == PLAY

            # Update insects if not in respawn phase
            if not respawning:
                for insect in insects:
                    insect.update(dt)
                    # ───────────────────────────────────────────────────
                    # Insect–insect collision: bounce like screen edges
                    # ───────────────────────────────────────────────────
                    for i in range(len(insects)):
                        for j in range(i+1, len(insects)):
                            a = insects[i]
                            b = insects[j]

                            # Compute vector between centers
                            ax = a.x + a.sprite_w/2
                            ay = a.y + a.sprite_h/2
                            bx = b.x + b.sprite_w/2
                            by = b.y + b.sprite_h/2
                            dx = ax - bx
                            dy = ay - by
                            dist2 = dx*dx + dy*dy
                            # minimum squared distance for a bounce (treat as circles)
                            min_dist = (a.sprite_w/2 + b.sprite_w/2)
                            if dist2 < min_dist*min_dist and dist2 > 0:
                                dist = math.sqrt(dist2)
                                # Normalize collision normal
                                nx = dx / dist
                                ny = dy / dist

                                # Relative velocity in normal direction
                                rvx = a.vx - b.vx
                                rvy = a.vy - b.vy
                                rel_norm = rvx * nx + rvy * ny

                                # If they’re moving toward each other, reflect
                                if rel_norm < 0:
                                    # Simple elastic: swap their normal components
                                    a.vx -= rel_norm * nx
                                    a.vy -= rel_norm * ny
                                    b.vx += rel_norm * nx
                                    b.vy += rel_norm * ny

                                    # Push them apart so they no longer overlap
                                    overlap = min_dist - dist
                                    a.x += nx * ( overlap/2 )
                                    a.y += ny * ( overlap/2 )
                                    b.x -= nx * ( overlap/2 )
                                    b.y -= ny * ( overlap/2 )

                                    # --- 3) Spawn a baby, but only if under the cap ---
                                if len(insects) < MAX_INSECTS:
                                    baby = Insect(a.screen_w, a.screen_h, a.pixel_size)

                                    # --- place baby just outside parent A ---
                                    parent_radius = a.sprite_w / 2
                                    baby_radius  = baby.sprite_w / 2
                                    safe_dist = parent_radius + baby_radius + 5

                                    # baby center = A center + normal*(parent_radius+baby_radius+ε)
                                    baby_cx = ax + nx * safe_dist
                                    baby_cy = ay + ny * safe_dist

                                    # convert to top-left:
                                    baby.x = baby_cx - baby_radius
                                    baby.y = baby_cy - baby_radius

                                    # clamp fully on-screen
                                    baby.x = max(0, min(baby.x, baby.screen_w - baby.sprite_w))
                                    baby.y = max(0, min(baby.y, baby.screen_h - baby.sprite_h))

                                    insects.append(baby)


            # Update particles
            for p in particles:
                p.update(dt)
            # Remove dead particles
            particles = [p for p in particles if p.age < p.life and p.size > 0]

            screen.fill((0, 0, 0))
            bg.draw(screen)

            # If respawning, draw rainbow flash then update the background, insects, respawning var, increment the level, update MAX_INSECTS
            if respawning:
                elapsed = (now_ms - respawn_start) / 1000.0
                frac = min(elapsed / RESPAWN_DURATION, 1.0)
                hue = frac  # cycle hue from 0 to 1
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                overlay_color = (int(r * 255), int(g * 255), int(b * 255))
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                alpha = int(255 * (1 - frac))
                overlay.fill((*overlay_color, alpha))
                screen.blit(overlay, (0, 0))
                if elapsed >= RESPAWN_DURATION:
                    bg = Background(width, height)
                    insects = new_batch()
                    respawning = False
                    level += 1
                    MAX_INSECTS = level

            # Draw insects when not respawning
            else:
                for insect in insects:
                    # 1) Get the current animated sprite (unrotated)
                    bug_surf = insect.render(t)

                    # 2) Compute the rotation angle (in degrees) so “up” → direction of (vx, vy)
                    #
                    #    We treat the original sprite as oriented “up” (0°).  We want to rotate it
                    #    CCW by (angle_of_up – angle_of_velocity), where:
                    #      angle_of_up = -90°  (i.e. atan2(-1, 0) in degrees)
                    #      angle_of_velocity = atan2(vy, vx) in degrees
                    #
                    #    So rotation = (-90°) - atan2(vy, vx)
                    ang_rad = math.atan2(insect.vy, insect.vx)
                    rot_deg = -90 - math.degrees(ang_rad)

                    # 3) Rotate the sprite (pygame.transform.rotate rotates CCW by given degrees)
                    rotated_surf = pygame.transform.rotate(bug_surf, rot_deg)

                    # 4) Compute a rect so that the rotated sprite’s center stays at the insect’s center
                    orig_center_x = insect.x + insect.sprite_w / 2
                    orig_center_y = insect.y + insect.sprite_h / 2
                    rotated_rect = rotated_surf.get_rect(center=(orig_center_x, orig_center_y))

                    # 5) Blit the rotated surface at its topleft
                    screen.blit(rotated_surf, rotated_rect.topleft)
                # draw special bug on top, spinning
                if special_bug:
                    base = special_bug.render(t)
                    age = (now_ms - special_bug.spawn_time) / 1000.0
                    angle = special_bug.spin_speed * age
                    rot = pygame.transform.rotate(base, angle)
                    # center at special_bug.x+half, special_bug.y+half
                    cx = special_bug.x + special_bug.sprite_w/2
                    cy = special_bug.y + special_bug.sprite_h/2
                    r = rot.get_rect(center=(cx, cy))
                    screen.blit(rot, r.topleft)
                    
            # 1) Draw score and level at top-center (score zero-padded to 7 digits, level zero-padded to 2 digits)
            score_text = f"{score:07d}"
            level_text = f"Level: {level:02d}"
            score_surf = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surf.get_rect(center=(width // 2 + 100, 20))
            level_surf = font.render(level_text, True, (255, 255, 255))
            level_rect = level_surf.get_rect(center=(width//2 - 100, 20))
            screen.blit(score_surf, score_rect)
            screen.blit(level_surf, level_rect)


            # 2) Draw particles on top
            for p in particles:
                p.draw(screen)

            # 3) Draw & update popups
            new_popups = []
            for popup in popups:
                elapsed = now_ms - popup["start"]
                if elapsed > POP_DURATION:
                    continue
                frac = elapsed / POP_DURATION
                alpha = int(255 * (1 - frac))
                y_off = -FLOAT_PIXELS * frac

                surf = popup["surf"].copy()
                surf.set_alpha(alpha)
                rect = surf.get_rect(center=(popup["x"], popup["y"] + y_off))
                screen.blit(surf, rect)

                new_popups.append(popup)
            popups = new_popups

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
