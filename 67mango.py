"""
Water Whack-a-Mole - Enhanced Edition
Arrow keys to aim
SPACE or mouse click to spray water
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
POINTS_PER_HIT = 10
GAME_DURATION = 60.0
NUM_HOLES = 4
HITS_TO_FILL = 3


# ─────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────
class Bot:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.timer = 0
        self.pop = 0

        # Water damage system
        self.water_hits = 0
        self.defeated = False
        self.defeat_timer = 0

    @property
    def body_y(self):
        return self.y + 40 * self.pop

    def draw(self):

        if self.pop <= 0:
            return

        text_color = arcade.color.WHITE

        # Change color while filling with water
        if self.water_hits == 1:
            text_color = arcade.color.AQUAMARINE

        elif self.water_hits >= 2:
            text_color = arcade.color.SKY_BLUE

        # Final soaked state
        if self.defeated:
            text_color = arcade.color.BLUE_BELL

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
        fill_percent = min(1, self.water_hits / HITS_TO_FILL)

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
# Water Stream
# ─────────────────────────────────────────────
class WaterShot:

    def __init__(self, start_x, start_y, target_x, target_y):

        self.x = start_x
        self.y = start_y

        angle = math.atan2(
            target_y - start_y,
            target_x - start_x
        )

        speed = 18

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.alive = True

        # Water trail
        self.trail = []

    def update(self):

        self.trail.append((self.x, self.y))

        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += self.dx
        self.y += self.dy

        if (
            self.x < 0 or
            self.x > WINDOW_WIDTH or
            self.y < 0 or
            self.y > WINDOW_HEIGHT
        ):
            self.alive = False

    def draw(self):

        # Draw stream trail
        for i, (tx, ty) in enumerate(self.trail):

            size = max(2, i)

            arcade.draw_circle_filled(
                tx,
                ty,
                size,
                (100, 220, 255)
            )

        # Main water head
        arcade.draw_circle_filled(
            self.x,
            self.y,
            8,
            arcade.color.SKY_BLUE
        )

        arcade.draw_circle_outline(
            self.x,
            self.y,
            11,
            arcade.color.WHITE,
            2
        )


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
        self.water_shots = []

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

        # Water guide
        arcade.draw_line(
            self.player_x + 30,
            self.player_y + 15,
            target_x,
            target_y,
            (120, 200, 255),
            4
        )

        arcade.draw_line(
            self.player_x + 30,
            self.player_y + 15,
            target_x,
            target_y,
            arcade.color.WHITE,
            1
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

        # Water stream
        for shot in self.water_shots:
            shot.draw()

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
            "← → to aim | SPACE or CLICK to spray",
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
            if bot.timer < VISIBLE_TIME or bot.defeated
        ]

        # Handle defeated bots
        for bot in self.bots[:]:

            if bot.defeated:

                bot.defeat_timer -= delta_time

                if bot.defeat_timer <= 0:

                    self.bots.remove(bot)

        # Update water
        for shot in self.water_shots:
            shot.update()

        self.water_shots = [
            shot for shot in self.water_shots
            if shot.alive
        ]

        # Collision detection
        for shot in self.water_shots:

            for bot in self.bots[:]:

                distance = math.hypot(
                    shot.x - bot.x,
                    shot.y - bot.body_y
                )

                if distance < 30 and not bot.defeated:

                    shot.alive = False

                    # Add water hit
                    bot.water_hits += 1

                    # Fully soaked
                    if bot.water_hits >= HITS_TO_FILL:

                        bot.defeated = True
                        bot.defeat_timer = 1.5

                        self.score += POINTS_PER_HIT

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

            self.shoot_water()

    # ─────────────────────────────────

    def on_mouse_press(self, x, y, button, modifiers):

        if self.game_over:

            self.reset()
            return

        self.shoot_water()

    # ─────────────────────────────────

    def shoot_water(self):

        if self.game_over:
            return

        target_x, target_y = HOLE_POSITIONS[self.current_tank]

        nozzle_x = self.player_x + 30
        nozzle_y = self.player_y + 15

        shot = WaterShot(
            nozzle_x,
            nozzle_y,
            target_x,
            target_y
        )

        self.water_shots.append(shot)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():

    WhackGame()
    arcade.run()


if __name__ == "__main__":
    main()
