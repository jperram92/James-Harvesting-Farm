import pygame
from support import import_folder
from settings import LAYERS, TILE_SIZE


class Animal(pygame.sprite.Sprite):
    def __init__(self, pos, group, folder_path, speed=50):
        super().__init__(group)
        
        # 🐾 Load Animations
        self.animations = import_folder(folder_path)
        if not self.animations:
            print(f"[ERROR] No animations found in {folder_path}. Using placeholder.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0))  # Placeholder red square
        else:
            self.frame_index = 0
            self.image = self.animations[self.frame_index]
        
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']
        
        # 🧭 Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = speed
        
    def animate(self, dt):
        """Animate the sprite."""
        if self.animations:
            self.frame_index += 4 * dt
            if self.frame_index >= len(self.animations):
                self.frame_index = 0
            self.image = self.animations[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


# 🦒 **Custom Giraffe Class with Box Movement**
class Giraffe(Animal):
    def __init__(self, pos, group):
        super().__init__(pos, group, 'graphics/animals/giraffe', speed=30)
        print(f"[DEBUG] Giraffe created at {pos}")
        
        # 🐾 Scale Giraffe Sprite
        self.scale_giraffe()
        
        # 📦 Box Movement Setup
        self.box_path = ['right', 'down', 'left', 'up']  # Movement sequence
        self.current_path_index = 0
        self.move_distance = 200  # Distance to move in each direction
        self.start_pos = pygame.math.Vector2(self.pos)
        self.has_reached_target = False

    def scale_giraffe(self):
        """Resize the giraffe sprite dynamically."""
        scaled_size = (TILE_SIZE * 1.5, TILE_SIZE * 1.5)  # Slightly larger
        self.animations = [pygame.transform.scale(frame, scaled_size) for frame in self.animations]
        self.image = self.animations[self.frame_index]
        self.image.set_colorkey((255, 255, 255))  # Remove white background

    def move(self, dt):
        """Move the giraffe in a box pattern."""
        direction = self.box_path[self.current_path_index]
        movement_vector = pygame.math.Vector2(0, 0)

        # Define movement based on current direction
        if direction == 'right':
            movement_vector.x = 1
        elif direction == 'down':
            movement_vector.y = 1
        elif direction == 'left':
            movement_vector.x = -1
        elif direction == 'up':
            movement_vector.y = -1

        # Move the giraffe
        self.pos += movement_vector * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Check if the giraffe has reached its target in the current direction
        if direction in ['right', 'left']:
            if abs(self.pos.x - self.start_pos.x) >= self.move_distance:
                self.has_reached_target = True
        elif direction in ['up', 'down']:
            if abs(self.pos.y - self.start_pos.y) >= self.move_distance:
                self.has_reached_target = True

        # Switch to the next path if the giraffe reaches its target
        if self.has_reached_target:
            self.has_reached_target = False
            self.current_path_index = (self.current_path_index + 1) % len(self.box_path)
            self.start_pos = pygame.math.Vector2(self.pos)  # Reset the start position for the next direction

    def update(self, dt):
        """Update Giraffe-specific movement and animation."""
        self.move(dt)
        self.animate(dt)

# **Custom Chicken Class with Box Movement**
class Chicken(Animal):
    def __init__(self, pos, group):
        super().__init__(pos, group, 'graphics/animals/chicken', speed=30)
        print(f"[DEBUG] Chicken created at {pos}")
        
        # 🐾 Scale Chicken Sprite
        self.scale_chicken()
        
        # 📦 Box Movement Setup
        self.box_path = ['right', 'down', 'left', 'up']  # Movement sequence
        self.current_path_index = 0
        self.move_distance = 200  # Distance to move in each direction
        self.start_pos = pygame.math.Vector2(self.pos)
        self.has_reached_target = False

    def scale_chicken(self):
        """Resize the giraffe sprite dynamically."""
        scaled_size = (TILE_SIZE * 1.5, TILE_SIZE * 1.5)  # Slightly larger
        self.animations = [pygame.transform.scale(frame, scaled_size) for frame in self.animations]
        self.image = self.animations[self.frame_index]
        self.image.set_colorkey((255, 255, 255))  # Remove white background

    def move(self, dt):
        """Move the chicken in a box pattern."""
        direction = self.box_path[self.current_path_index]
        movement_vector = pygame.math.Vector2(0, 0)

        # Define movement based on current direction
        if direction == 'right':
            movement_vector.x = 1
        elif direction == 'down':
            movement_vector.y = 1
        elif direction == 'left':
            movement_vector.x = -1
        elif direction == 'up':
            movement_vector.y = -1

        # Move the chicken
        self.pos += movement_vector * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Check if the chicken has reached its target in the current direction
        if direction in ['right', 'left']:
            if abs(self.pos.x - self.start_pos.x) >= self.move_distance:
                self.has_reached_target = True
        elif direction in ['up', 'down']:
            if abs(self.pos.y - self.start_pos.y) >= self.move_distance:
                self.has_reached_target = True

        # Switch to the next path if the chicken reaches its target
        if self.has_reached_target:
            self.has_reached_target = False
            self.current_path_index = (self.current_path_index + 1) % len(self.box_path)
            self.start_pos = pygame.math.Vector2(self.pos)  # Reset the start position for the next direction

    def update(self, dt):
        """Update chicken-specific movement and animation."""
        self.move(dt)
        self.animate(dt)