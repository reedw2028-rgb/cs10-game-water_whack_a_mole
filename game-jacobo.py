import arcade
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Water Hose Blob Game"

PLAYER_SPEED = 5
SHOT_SPEED = 10
BLOB_SPAWN_TIME = 60  # frames

# --- Sprites ---
class Player(arcade.Sprite):
    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Keep player on screen
        self.center_x = max(0, min(SCREEN_WIDTH, self.center_x))
        self.center_y = max(0, min(SCREEN_HEIGHT, self.center_y))


class Blob(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/enemies/slimePurple.png", 0.5)
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = random.randint(200, SCREEN_HEIGHT - 50)
        self.timer = 120  # lifespan

    def update(self, delta_time: float = 1/60):
        self.timer -= 1
        if self.timer <= 0:
            self.remove_from_sprite_lists()


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.player = None
        self.player_list = None
        self.blob_list = None
        self.shot_list = None

        self.score = 0
        self.frame_count = 0

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.blob_list = arcade.SpriteList()
        self.shot_list = arcade.SpriteList()

        self.player = Player(":resources:images/animated_characters/male_person/malePerson_idle.png", 0.5)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 50
        self.player_list.append(self.player)

        self.score = 0
        self.frame_count = 0

    def on_draw(self):
        self.clear()

        self.player_list.draw()
        self.blob_list.draw()
        self.shot_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.frame_count += 1

        # Spawn blobs
        if self.frame_count % BLOB_SPAWN_TIME == 0:
            blob = Blob()
            self.blob_list.append(blob)

        self.player_list.update()
        self.blob_list.update()
        self.shot_list.update()

        # Move shots upward
        for shot in self.shot_list:
            shot.center_y += SHOT_SPEED
            if shot.center_y > SCREEN_HEIGHT:
                shot.remove_from_sprite_lists()

        # Collision detection
        for shot in self.shot_list:
            hit_list = arcade.check_for_collision_with_list(shot, self.blob_list)
            for blob in hit_list:
                blob.remove_from_sprite_lists()
                shot.remove_from_sprite_lists()
                self.score += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.DOWN:
            self.player.change_y = -PLAYER_SPEED

        # Shoot water (spacebar)
        elif key == arcade.key.SPACE:
            shot = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", 0.5)
            shot.center_x = self.player.center_x
            shot.center_y = self.player.center_y + 20
            self.shot_list.append(shot)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player.change_x = 0
        elif key in [arcade.key.UP, arcade.key.DOWN]:
            self.player.change_y = 0


def main():
    game = Game()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
