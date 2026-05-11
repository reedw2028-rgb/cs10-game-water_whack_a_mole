"""
Water Whack-a-Mole - Enhanced Edition
Arrow keys to aim
Hold SPACE or mouse click to spray water
"""

import arcade
import random
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Water Whack-a-Mole"

# Hole positions
HOLE_POSITIONS = [
    (140, 470),
    (320, 470),
    (500, 470),
    (680, 470)
]

# Gameplay settings
SPAWN_INTERVAL = 2.5
MIN_SPAWN_INTERVAL = 0.75
SPAWN_SPEEDUP_PER_SECOND = 0.025
VISIBLE_TIME = 4.5
POINTS_PER_DATA_CENTER = 10
NUM_HOLES = 4
WATER_FILL_SECONDS = 1.0
WATER_DRAIN_PER_SECOND = 0.022


# ─────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────
class Bot:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.timer = 0
        self.pop = 0

        # Water requirement system
        self.water_fill = 0.0
        self.shut_down = False

    @property
    def body_y(self):
        return self.y + 40 * self.pop

    def draw(self, is_being_sprayed=False):

        if self.pop <= 0:
            return

        text_color = arcade.color.WHITE

        # Change color while filling with water
        if self.shut_down:
            text_color = (255, 105, 105)

        elif self.water_fill >= 0.7:
            text_color = arcade.color.SKY_BLUE

        elif self.water_fill >= 0.35:
            text_color = arcade.color.AQUAMARINE

        # Shadow
        arcade.draw_lbwh_rectangle_filled(
            self.x - 58,
            self.body_y - 19,
            116,
            42,
            (15, 20, 35)
        )

        outline_color = arcade.color.RED if self.shut_down else arcade.color.SKY_BLUE

        arcade.draw_lbwh_rectangle_outline(
            self.x - 58,
            self.body_y - 19,
            116,
            42,
            outline_color,
            2
        )

        # Target label
        arcade.draw_text(
            "SHUT" if self.shut_down else "DATA",
            self.x,
            self.body_y + 7,
            text_color,
            15,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            "DOWN" if self.shut_down else "CENTER",
            self.x,
            self.body_y - 9,
            text_color,
            13,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Water fill bar
        bar_width = 96
        bar_height = 12
        bar_x = self.x - bar_width / 2
        bar_y = self.body_y - 36
        fill_percent = min(1, self.water_fill)
        bar_outline_color = arcade.color.RED if self.shut_down else arcade.color.WHITE
        bar_fill_color = (180, 45, 45) if self.shut_down else (70, 205, 255)

        if is_being_sprayed:
            bar_outline_color = arcade.color.YELLOW
            bar_fill_color = (135, 235, 255)

        arcade.draw_lbwh_rectangle_filled(
            bar_x,
            bar_y,
            bar_width,
            bar_height,
            (25, 35, 55)
        )

        arcade.draw_lbwh_rectangle_filled(
            bar_x,
            bar_y,
            bar_width * fill_percent,
            bar_height,
            bar_fill_color
        )

        arcade.draw_lbwh_rectangle_outline(
            bar_x,
            bar_y,
            bar_width,
            bar_height,
            bar_outline_color,
            2
        )


# ─────────────────────────────────────────────
# Water Helper
# ─────────────────────────────────────────────
def distance_to_line_segment(px, py, x1, y1, x2, y2):

    line_dx = x2 - x1
    line_dy = y2 - y1
    line_length = line_dx * line_dx + line_dy * line_dy

    if line_length == 0:
        return math.hypot(px - x1, py - y1)

    point_position = (
        (px - x1) * line_dx + (py - y1) * line_dy
    ) / line_length

    point_position = max(0, min(1, point_position))

    closest_x = x1 + point_position * line_dx
    closest_y = y1 + point_position * line_dy

    return math.hypot(px - closest_x, py - closest_y)


# ─────────────────────────────────────────────
# Main Game
# ─────────────────────────────────────────────
class WhackGame(arcade.Window):

    def __init__(self):

        super().__init__(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            WINDOW_TITLE
        )

        arcade.set_background_color((40, 30, 70))

        # Player position
        self.player_x = WINDOW_WIDTH // 2 - 80
        self.player_y = 90

        # Tank position
        self.tank_x = self.player_x + 150
        self.tank_y = self.player_y + 20

        # Selected target hole
        self.current_tank = 0

        self.reset()

    # ─────────────────────────────────

    def reset(self):

        self.score = 0
        self.spawn_timer = 0
        self.elapsed_time = 0

        self.game_over = False

        self.bots = []
        self.spraying = False
        self.water_level = 1.0

    # ─────────────────────────────────

    def get_spawn_interval(self):

        return max(
            MIN_SPAWN_INTERVAL,
            SPAWN_INTERVAL - self.elapsed_time * SPAWN_SPEEDUP_PER_SECOND
        )

    # ─────────────────────────────────

    def get_time_text(self):

        total_seconds = int(self.elapsed_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes}:{seconds:02d}"

    # ─────────────────────────────────

    def draw_water_tank(self):

        x = self.tank_x
        y = self.tank_y
        tank_width = 68
        tank_height = 112
        tank_x = x - tank_width / 2
        tank_y = y - tank_height / 2
        water_padding = 5
        water_width = tank_width - water_padding * 2
        water_max_height = tank_height - water_padding * 2
        water_height = water_max_height * self.water_level

        # Tank body
        arcade.draw_lbwh_rectangle_filled(
            tank_x,
            tank_y,
            tank_width,
            tank_height,
            (80, 120, 165)
        )

        arcade.draw_lbwh_rectangle_outline(
            tank_x,
            tank_y,
            tank_width,
            tank_height,
            arcade.color.DARK_BLUE,
            3
        )

        # Water inside
        if water_height > 0:
            arcade.draw_lbwh_rectangle_filled(
                tank_x + water_padding,
                tank_y + water_padding,
                water_width,
                water_height,
                (80, 200, 255)
            )

        arcade.draw_lbwh_rectangle_outline(
            tank_x + water_padding,
            tank_y + water_padding,
            water_width,
            water_max_height,
            (185, 235, 255),
            2
        )

        # Cap
        arcade.draw_circle_filled(
            x,
            tank_y + tank_height + 5,
            12,
            arcade.color.DARK_GRAY
        )

    # ─────────────────────────────────

    def draw_hose_to_target(self):

        target_x, target_y = HOLE_POSITIONS[self.current_tank]
        spray_target = self.get_spray_target()

        if spray_target is not None:
            target_x = spray_target.x
            target_y = spray_target.body_y

        hose_start_x = self.tank_x - 34
        hose_start_y = self.tank_y

        # Main hose
        arcade.draw_line(
            hose_start_x,
            hose_start_y,
            self.player_x + 30,
            self.player_y + 15,
            arcade.color.DARK_GRAY,
            7
        )

        # Highlight
        arcade.draw_line(
            hose_start_x,
            hose_start_y,
            self.player_x + 30,
            self.player_y + 15,
            (150, 150, 150),
            3
        )

        # Nozzle
        arcade.draw_circle_filled(
            self.player_x + 30,
            self.player_y + 15,
            6,
            arcade.color.DARK_GRAY
        )

        if self.spraying and self.water_level > 0:

            # Continuous water blast
            arcade.draw_line(
                self.player_x + 30,
                self.player_y + 15,
                target_x,
                target_y,
                (65, 190, 255),
                16
            )

            arcade.draw_line(
                self.player_x + 30,
                self.player_y + 15,
                target_x,
                target_y,
                (145, 235, 255),
                9
            )

            arcade.draw_line(
                self.player_x + 30,
                self.player_y + 15,
                target_x,
                target_y,
                arcade.color.WHITE,
                3
            )

            arcade.draw_circle_filled(
                target_x,
                target_y,
                17,
                (105, 225, 255)
            )

            arcade.draw_circle_outline(
                target_x,
                target_y,
                24,
                arcade.color.WHITE,
                3
            )

        else:

            # Aim guide
            arcade.draw_line(
                self.player_x + 30,
                self.player_y + 15,
                target_x,
                target_y,
                (120, 200, 255),
                2
            )

        # Target indicator
        arcade.draw_circle_outline(
            target_x,
            target_y,
            35,
            arcade.color.YELLOW,
            2
        )

    # ─────────────────────────────────

    def draw_player(self):

        x = self.player_x
        y = self.player_y

        # Legs
        arcade.draw_line(
            x - 15,
            y - 40,
            x - 5,
            y - 80,
            arcade.color.BLACK,
            5
        )

        arcade.draw_line(
            x + 15,
            y - 40,
            x + 5,
            y - 80,
            arcade.color.BLACK,
            5
        )

        # Body
        arcade.draw_lbwh_rectangle_filled(
            x - 20,
            y - 30,
            40,
            60,
            arcade.color.BLUE
        )

        # Arms
        arcade.draw_line(
            x - 20,
            y + 10,
            x + 20,
            y + 10,
            arcade.color.BLACK,
            5
        )

        arcade.draw_line(
            x + 20,
            y + 10,
            x + 35,
            y - 15,
            arcade.color.BLACK,
            5
        )

        # Head
        arcade.draw_circle_filled(
            x,
            y + 55,
            20,
            arcade.color.BISQUE
        )

        # Eyes
        arcade.draw_circle_filled(
            x - 6,
            y + 60,
            2,
            arcade.color.BLACK
        )

        arcade.draw_circle_filled(
            x + 6,
            y + 60,
            2,
            arcade.color.BLACK
        )

    # ─────────────────────────────────

    def on_draw(self):

        self.clear()

        # Ground
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            WINDOW_WIDTH,
            160,
            (55, 45, 90)
        )

        # Holes
        for i, (x, y) in enumerate(HOLE_POSITIONS):

            arcade.draw_ellipse_filled(
                x,
                y,
                110,
                35,
                (60, 35, 20)
            )

            arcade.draw_ellipse_outline(
                x,
                y,
                110,
                35,
                arcade.color.BLACK,
                3
            )

            # Selected hole highlight
            if i == self.current_tank:

                arcade.draw_ellipse_outline(
                    x,
                    y,
                    120,
                    45,
                    arcade.color.YELLOW,
                    4
                )

        active_spray_target = self.get_spray_target() if self.spraying else None

        # Bots
        for bot in self.bots:
            bot.draw(bot is active_spray_target)

        # Tank
        self.draw_water_tank()

        # Hose
        self.draw_hose_to_target()

        # Player
        self.draw_player()

        # HUD
        arcade.draw_lbwh_rectangle_filled(
            590,
            5,
            190,
            75,
            (20, 20, 40)
        )

        arcade.draw_text(
            f"SCORE: {self.score}",
            610,
            55,
            arcade.color.YELLOW,
            18,
            bold=True
        )

        arcade.draw_text(
            f"WATER: {int(self.water_level * 100)}%",
            610,
            25,
            (80, 200, 255),
            18,
            bold=True
        )

        arcade.draw_text(
            "WATER WHACK",
            20,
            25,
            arcade.color.WHITE,
            24,
            bold=True
        )

        arcade.draw_text(
            "← → to aim | Hold SPACE or CLICK to spray",
            20,
            530,
            arcade.color.LIGHT_GRAY,
            12
        )

        # Timer
        arcade.draw_lbwh_rectangle_filled(
            600,
            525,
            180,
            55,
            (20, 20, 40)
        )

        arcade.draw_text(
            f"TIME: {self.get_time_text()}",
            690,
            552,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Game Over
        if self.game_over:

            arcade.draw_lbwh_rectangle_filled(
                200,
                200,
                400,
                200,
                (0, 0, 0)
            )

            arcade.draw_text(
                "GAME OVER",
                250,
                330,
                arcade.color.WHITE,
                40,
                bold=True
            )

            arcade.draw_text(
                f"FINAL SCORE: {self.score}",
                260,
                280,
                arcade.color.YELLOW,
                18
            )

            arcade.draw_text(
                "CLICK or SPACE to RESTART",
                245,
                230,
                arcade.color.LIGHT_GRAY,
                14
            )

    # ─────────────────────────────────

    def on_update(self, delta_time):

        if self.game_over:
            return

        self.elapsed_time += delta_time

        # Spawn bots
        self.spawn_timer += delta_time

        if self.spawn_timer >= self.get_spawn_interval():

            self.spawn_timer = 0
            self.spawn_bot()

        self.update_water_stream(delta_time)

        # Update bots
        for bot in self.bots:

            if bot.shut_down:
                bot.pop = 1
                continue

            bot.timer += delta_time

            bot.pop = min(
                1,
                bot.timer / 0.25
            )

            if bot.timer >= VISIBLE_TIME and bot.water_fill < 1:
                bot.shut_down = True

        if self.all_lanes_shut_down():
            self.game_over = True
            self.stop_spraying()
            return

    # ─────────────────────────────────

    def spawn_bot(self):

        open_positions = [
            position for position in HOLE_POSITIONS
            if not self.has_bot_in_lane(position)
        ]

        if not open_positions:
            return

        x, y = random.choice(open_positions)

        self.bots.append(Bot(x, y))

    # ─────────────────────────────────

    def has_bot_in_lane(self, position):

        lane_x, lane_y = position

        for bot in self.bots:

            if bot.x == lane_x and bot.y == lane_y:
                return True

        return False

    # ─────────────────────────────────

    def all_lanes_shut_down(self):

        shut_down_lanes = {
            (bot.x, bot.y)
            for bot in self.bots
            if bot.shut_down
        }

        return len(shut_down_lanes) == NUM_HOLES

    # ─────────────────────────────────

    def on_key_press(self, key, modifiers):

        if self.game_over:

            if key == arcade.key.SPACE:
                self.reset()

            return

        if key == arcade.key.LEFT:

            self.current_tank = (
                self.current_tank - 1
            ) % NUM_HOLES

        elif key == arcade.key.RIGHT:

            self.current_tank = (
                self.current_tank + 1
            ) % NUM_HOLES

        elif key == arcade.key.SPACE:

            self.start_spraying()

    # ─────────────────────────────────

    def on_key_release(self, key, modifiers):

        if key == arcade.key.SPACE:
            self.stop_spraying()

    # ─────────────────────────────────

    def on_mouse_press(self, x, y, button, modifiers):

        if self.game_over:

            self.reset()
            return

        self.start_spraying()

    # ─────────────────────────────────

    def on_mouse_release(self, x, y, button, modifiers):

        self.stop_spraying()

    # ─────────────────────────────────

    def start_spraying(self):

        if self.game_over:
            return

        if self.water_level <= 0:
            return

        self.spraying = True

    # ─────────────────────────────────

    def stop_spraying(self):

        self.spraying = False

    # ─────────────────────────────────

    def update_water_stream(self, delta_time):

        if not self.spraying:
            return

        self.water_level = max(
            0,
            self.water_level - WATER_DRAIN_PER_SECOND * delta_time
        )

        if self.water_level <= 0:
            self.stop_spraying()
            return

        target_bot = self.get_spray_target()

        if target_bot is None:
            return

        target_bot.water_fill = min(
            1,
            target_bot.water_fill + delta_time / WATER_FILL_SECONDS
        )

        if target_bot.water_fill >= 1:

            self.score += POINTS_PER_DATA_CENTER
            self.bots.remove(target_bot)

    # ─────────────────────────────────

    def get_spray_target(self):

        target_x, target_y = HOLE_POSITIONS[self.current_tank]

        best_bot = None
        best_fill = -1
        best_timer = -1

        for bot in self.bots:

            if bot.shut_down:
                continue

            if bot.x != target_x or bot.y != target_y:
                continue

            if (
                bot.water_fill > best_fill or
                (bot.water_fill == best_fill and bot.timer > best_timer)
            ):
                best_bot = bot
                best_fill = bot.water_fill
                best_timer = bot.timer

        return best_bot

    # ─────────────────────────────────

    def shoot_water(self):

        self.start_spraying()


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():

    WhackGame()
    arcade.run()


if __name__ == "__main__":
    main()





























































































































