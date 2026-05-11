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
VISIBLE_TIME = 4.5
POINTS_PER_DATA_CENTER = 10
GAME_DURATION = 60.0
NUM_HOLES = 4
WATER_FILL_SECONDS = 1.2


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

    @property
    def body_y(self):
        return self.y + 40 * self.pop

    def draw(self):

        if self.pop <= 0:
            return

        text_color = arcade.color.WHITE

        # Change color while filling with water
        if self.water_fill >= 0.7:
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

        arcade.draw_lbwh_rectangle_outline(
            self.x - 58,
            self.body_y - 19,
            116,
            42,
            arcade.color.SKY_BLUE,
            2
        )

        # Target label
        arcade.draw_text(
            "DATA",
            self.x,
            self.body_y + 7,
            text_color,
            15,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            "CENTER",
            self.x,
            self.body_y - 9,
            text_color,
            13,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Water fill bar
        bar_width = 86
        bar_height = 10
        bar_x = self.x - bar_width / 2
        bar_y = self.body_y - 36
        fill_percent = min(1, self.water_fill)

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
            (70, 205, 255)
        )

        arcade.draw_lbwh_rectangle_outline(
            bar_x,
            bar_y,
            bar_width,
            bar_height,
            arcade.color.WHITE,
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
        self.time_left = GAME_DURATION
        self.spawn_timer = 0

        self.game_over = False

        self.bots = []
        self.spraying = False

    # ─────────────────────────────────

    def draw_water_tank(self):

        x = self.tank_x
        y = self.tank_y

        # Tank body
        arcade.draw_lbwh_rectangle_filled(
            x - 20,
            y - 30,
            40,
            60,
            (100, 150, 200)
        )

        arcade.draw_lbwh_rectangle_outline(
            x - 20,
            y - 30,
            40,
            60,
            arcade.color.DARK_BLUE,
            3
        )

        # Water inside
        arcade.draw_lbwh_rectangle_filled(
            x - 18,
            y - 28,
            36,
            45,
            (80, 200, 255)
        )

        # Cap
        arcade.draw_circle_filled(
            x,
            y + 30,
            9,
            arcade.color.DARK_GRAY
        )

    # ─────────────────────────────────

    def draw_hose_to_target(self):

        target_x, target_y = HOLE_POSITIONS[self.current_tank]
        spray_target = self.get_spray_target()

        if spray_target is not None:
            target_x = spray_target.x
            target_y = spray_target.body_y

        hose_start_x = self.tank_x - 18
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

        if self.spraying:

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

        # Bots
        for bot in self.bots:
            bot.draw()

        # Tank
        self.draw_water_tank()

        # Hose
        self.draw_hose_to_target()

        # Player
        self.draw_player()

        # HUD
        arcade.draw_lbwh_rectangle_filled(
            590,
            10,
            190,
            80,
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
            f"TIME: {int(self.time_left)}",
            610,
            25,
            arcade.color.SKY_BLUE,
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

        self.time_left -= delta_time

        if self.time_left <= 0:

            self.game_over = True
            return

        # Spawn bots
        self.spawn_timer += delta_time

        if self.spawn_timer >= SPAWN_INTERVAL:

            self.spawn_timer = 0
            self.spawn_bot()

        # Update bots
        for bot in self.bots:

            bot.timer += delta_time

            bot.pop = min(
                1,
                bot.timer / 0.25
            )

        # Remove timed-out bots
        self.bots = [
            bot for bot in self.bots
            if bot.timer < VISIBLE_TIME
        ]

        self.update_water_stream(delta_time)

    # ─────────────────────────────────

    def spawn_bot(self):

        x, y = random.choice(HOLE_POSITIONS)

        self.bots.append(Bot(x, y))

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

        self.spraying = True

    # ─────────────────────────────────

    def stop_spraying(self):

        self.spraying = False

    # ─────────────────────────────────

    def update_water_stream(self, delta_time):

        if not self.spraying:
            return

        target_bot = self.get_spray_target()

        if target_bot is None:
            return

        target_bot.water_fill += delta_time / WATER_FILL_SECONDS

        if target_bot.water_fill >= 1:

            self.score += POINTS_PER_DATA_CENTER
            self.bots.remove(target_bot)

    # ─────────────────────────────────

    def get_spray_target(self):

        nozzle_x = self.player_x + 30
        nozzle_y = self.player_y + 15
        target_x, target_y = HOLE_POSITIONS[self.current_tank]

        best_bot = None
        best_distance = 999999
        best_progress = 999999

        for bot in self.bots:

            distance = distance_to_line_segment(
                bot.x,
                bot.body_y,
                nozzle_x,
                nozzle_y,
                target_x,
                target_y
            )

            if distance > 35:
                continue

            progress = math.hypot(
                bot.x - nozzle_x,
                bot.body_y - nozzle_y
            )

            if (
                distance < best_distance or
                (distance == best_distance and progress < best_progress)
            ):
                best_bot = bot
                best_distance = distance
                best_progress = progress

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
