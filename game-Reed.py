"""
Whack-a-Bot Water Hose Edition
"""

import arcade
import random
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Whack-a-Bot!"

# ONLY 4 HOLES
HOLE_POSITIONS = [
    (150, 450),
    (320, 450),
    (490, 450),
    (660, 450)
]

SPAWN_INTERVAL = 1.2
VISIBLE_TIME = 2.0
POINTS_PER_HIT = 10
GAME_DURATION = 30.0

# YOUR IMAGE
PLAYER_IMAGE = "/Users/reed/Desktop/school_vscode/cs50-workspace-no-prior-cs50/photo_paper_dudejpeg.jpeg"


# ─────────────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────────────
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

        arcade.draw_circle_filled(
            self.x,
            self.body_y,
            25,
            arcade.color.GREEN
        )


# ─────────────────────────────────────────────────────
# Water Projectile
# ─────────────────────────────────────────────────────
class WaterShot:
    def __init__(self, start_x, start_y, target_x, target_y):

        self.x = start_x
        self.y = start_y

        angle = math.atan2(target_y - start_y, target_x - start_x)

        speed = 10

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Remove if off screen
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
            6,
            arcade.color.SKY_BLUE
        )


# ─────────────────────────────────────────────────────
# Main Game
# ─────────────────────────────────────────────────────
class WhackGame(arcade.Window):

    def __init__(self):

        super().__init__(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            WINDOW_TITLE
        )

        arcade.set_background_color((30, 20, 60))

        # Load player image
        self.player_texture = arcade.load_texture(PLAYER_IMAGE)

        # STATIONARY PLAYER POSITION
        self.player_x = 100
        self.player_y = 100

        # Smaller image size
        self.player_width = 120
        self.player_height = 120

        self.mouse_x = 0
        self.mouse_y = 0

        self.reset()

    def reset(self):

        self.score = 0
        self.time_left = GAME_DURATION
        self.spawn_timer = 0
        self.game_over = False

        self.bots = []
        self.water_shots = []

    # ─────────────────────────────────────────

    def on_draw(self):

        self.clear()

        # Draw holes
        for x, y in HOLE_POSITIONS:

            arcade.draw_ellipse_filled(
                x,
                y,
                100,
                30,
                arcade.color.DARK_BROWN
            )

        # Draw bots
        for bot in self.bots:
            bot.draw()

        # Draw water shots
        for shot in self.water_shots:
            shot.draw()

        # HUD
        arcade.draw_text(
            f"SCORE: {self.score}",
            20,
            560,
            arcade.color.YELLOW,
            18
        )

        arcade.draw_text(
            f"TIME: {int(self.time_left)}",
            650,
            560,
            arcade.color.CYAN,
            18
        )

        # Game over
        if self.game_over:

            arcade.draw_text(
                "GAME OVER",
                280,
                300,
                arcade.color.WHITE,
                32
            )

        # Draw stationary player
        arcade.draw_texture_rect(
            self.player_texture,
            arcade.rect.XYWH(
                self.player_x,
                self.player_y,
                self.player_width,
                self.player_height
            )
        )

    # ─────────────────────────────────────────

    def on_update(self, delta_time):

        if self.game_over:
            return

        # Timer
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

            bot.pop = min(1, bot.timer / 0.25)

        # Remove old bots
        self.bots = [
            bot for bot in self.bots
            if bot.timer < VISIBLE_TIME
        ]

        # Update water shots
        for shot in self.water_shots:
            shot.update()

        # Remove dead shots
        self.water_shots = [
            s for s in self.water_shots
            if s.alive
        ]

        # Collision detection
        for shot in self.water_shots:

            for bot in self.bots:

                distance = math.hypot(
                    shot.x - bot.x,
                    shot.y - bot.body_y
                )

                if distance < 30:

                    self.score += POINTS_PER_HIT

                    if bot in self.bots:
                        self.bots.remove(bot)

                    shot.alive = False

    # ─────────────────────────────────────────

    def spawn_bot(self):

        x, y = random.choice(HOLE_POSITIONS)

        self.bots.append(Bot(x, y))

    # ─────────────────────────────────────────

    def on_mouse_motion(self, x, y, dx, dy):

        self.mouse_x = x
        self.mouse_y = y

    # ─────────────────────────────────────────

    def on_mouse_press(self, x, y, button, modifiers):

        if self.game_over:

            self.reset()
            return

        # Shoot water
        water = WaterShot(
            self.player_x,
            self.player_y,
            x,
            y
        )

        self.water_shots.append(water)


# ─────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────
def main():

    WhackGame()
    arcade.run()


if __name__ == "__main__":
    main()
