"""
Water Whack-a-Mole - Enhanced Edition
Left/Right arrow keys to select tank
Click or SPACE to shoot water
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

SPAWN_INTERVAL = 1.2
VISIBLE_TIME = 2.0
POINTS_PER_HIT = 10
GAME_DURATION = 30.0
NUM_HOLES = 4


# ─────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────
class Bot:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.timer = 0
        self.pop = 0

    @property
    def body_y(self):
        return self.y + 40 * self.pop

    def draw(self):

        if self.pop <= 0:
            return

        # Shadow
        arcade.draw_circle_filled(
            self.x + 4,
            self.body_y - 4,
            25,
            (20, 80, 20)
        )

        # Body
        arcade.draw_circle_filled(
            self.x,
            self.body_y,
            25,
            arcade.color.LIME_GREEN
        )

        # Eyes
        arcade.draw_circle_filled(
            self.x - 8,
            self.body_y + 6,
            4,
            arcade.color.BLACK
        )

        arcade.draw_circle_filled(
            self.x + 8,
            self.body_y + 6,
            4,
            arcade.color.BLACK
        )


# ─────────────────────────────────────────────
# Water Projectile
# ─────────────────────────────────────────────
class WaterShot:

    def __init__(self, start_x, start_y, target_x, target_y):

        self.x = start_x
        self.y = start_y

        angle = math.atan2(
            target_y - start_y,
            target_x - start_x
        )

        speed = 12

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.alive = True

    def update(self):

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

        arcade.draw_circle_filled(
            self.x,
            self.y,
            7,
            arcade.color.SKY_BLUE
        )

        arcade.draw_circle_outline(
            self.x,
            self.y,
            10,
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

        # Tank position (to the right of player)
        self.tank_x = self.player_x + 150
        self.tank_y = self.player_y + 20

        # Currently selected tank index (0-3)
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
        """Draw the water tank on the right side"""

        x = self.tank_x
        y = self.tank_y

        # Tank body (large rectangle)
        arcade.draw_lbwh_rectangle_filled(
            x - 20,
            y - 30,
            40,
            60,
            (100, 150, 200)
        )

        # Tank outline
        arcade.draw_lbwh_rectangle_outline(
            x - 20,
            y - 30,
            40,
            60,
            arcade.color.DARK_BLUE,
            3
        )

        # Water level inside tank
        water_level = 45
        arcade.draw_lbwh_rectangle_filled(
            x - 18,
            y - 28,
            36,
            water_level,
            (80, 200, 255)
        )

        # Tank cap
        arcade.draw_circle_filled(
            x,
            y + 30,
            9,
            arcade.color.DARK_GRAY
        )

        # Hose connection point
        arcade.draw_circle_filled(
            x - 18,
            y,
            6,
            arcade.color.DARK_GRAY
        )

    def draw_hose_to_target(self):
        """Draw the hose from tank to selected hole"""

        # Get the target hole position
        target_x, target_y = HOLE_POSITIONS[self.current_tank]

        # Hose starts from tank connection
        hose_start_x = self.tank_x - 18
        hose_start_y = self.tank_y

        # Draw main hose line (thick)
        arcade.draw_line(
            hose_start_x,
            hose_start_y,
            self.player_x + 30,
            self.player_y + 15,
            arcade.color.DARK_GRAY,
            7
        )

        # Hose highlight (lighter line)
        arcade.draw_line(
            hose_start_x,
            hose_start_y,
            self.player_x + 30,
            self.player_y + 15,
            (150, 150, 150),
            3
        )

        # Nozzle at player's hands
        arcade.draw_circle_filled(
            self.player_x + 30,
            self.player_y + 15,
            6,
            arcade.color.DARK_GRAY
        )

        # Nozzle tip
        arcade.draw_circle_filled(
            self.player_x + 30,
            self.player_y + 15,
            3,
            arcade.color.BLACK
        )

        # Draw aiming indicator line to target hole
        arcade.draw_line(
            self.player_x + 30,
            self.player_y + 15,
            target_x,
            target_y,
            arcade.color.YELLOW,
            2
        )

        # Crosshair at target
        arcade.draw_circle_outline(
            target_x,
            target_y,
            35,
            arcade.color.YELLOW,
            2
        )

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

        # Left arm (holding nozzle)
        arcade.draw_line(
            x - 20,
            y + 10,
            x + 20,
            y + 10,
            arcade.color.BLACK,
            5
        )

        # Right arm
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

        # Draw holes with indicators
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

            # Highlight current target
            if i == self.current_tank:
                arcade.draw_ellipse_outline(
                    x,
                    y,
                    120,
                    45,
                    arcade.color.YELLOW,
                    4
                )

        # Draw bots
        for bot in self.bots:
            bot.draw()

        # Draw water
        for shot in self.water_shots:
            shot.draw()

        # Draw water tank
        self.draw_water_tank()

        # Draw hose and aiming line
        self.draw_hose_to_target()

        # Draw player
        self.draw_player()

        # HUD background
        arcade.draw_lbwh_rectangle_filled(
            590,
            10,
            190,
            80,
            (20, 20, 40)
        )

        # Score
        arcade.draw_text(
            f"SCORE: {self.score}",
            610,
            55,
            arcade.color.YELLOW,
            18,
            bold=True
        )

        # Time
        arcade.draw_text(
            f"TIME: {int(self.time_left)}",
            610,
            25,
            arcade.color.SKY_BLUE,
            18,
            bold=True
        )

        # Title
        arcade.draw_text(
            "WATER WHACK",
            20,
            25,
            arcade.color.WHITE,
            24,
            bold=True
        )

        # Control instructions
        arcade.draw_text(
            "← → Arrows to select | Space/Click to shoot",
            20,
            530,
            arcade.color.LIGHT_GRAY,
            12
        )

        # Game over
        if self.game_over:

            arcade.draw_rectangle_filled(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2,
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

        # Remove old bots
        self.bots = [
            bot for bot in self.bots
            if bot.timer < VISIBLE_TIME
        ]

        # Update water shots
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

                if distance < 30:

                    self.score += POINTS_PER_HIT

                    self.bots.remove(bot)

                    shot.alive = False

    # ─────────────────────────────────

    def spawn_bot(self):

        x, y = random.choice(HOLE_POSITIONS)

        self.bots.append(
            Bot(x, y)
        )

    # ─────────────────────────────────

    def on_key_press(self, key, modifiers):
        """Handle key press"""

        if self.game_over:
            if key == arcade.key.SPACE:
                self.reset()
            return

        # Left arrow - select previous tank
        if key == arcade.key.LEFT:
            self.current_tank = (self.current_tank - 1) % NUM_HOLES

        # Right arrow - select next tank
        elif key == arcade.key.RIGHT:
            self.current_tank = (self.current_tank + 1) % NUM_HOLES

        # Spacebar to shoot
        elif key == arcade.key.SPACE:
            self.shoot_water()

    def on_mouse_press(self, x, y, button, modifiers):

        if self.game_over:
            self.reset()
            return

        # Click to shoot
        self.shoot_water()

    def shoot_water(self):
        """Fire water shot at the selected hole"""

        if self.game_over:
            return

        # Get target hole
        target_x, target_y = HOLE_POSITIONS[self.current_tank]

        # Nozzle position
        nozzle_x = self.player_x + 30
        nozzle_y = self.player_y + 15

        # Create water shot
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
