import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import * 
from transition import Transition
from soil import SoilLayer
from sky import * 
from random import *
from menu import *
from save_system import SaveSystem
from animals import *


class Level:
    def __init__(self):
        #level to display to the main screen  - get display surface
        self.display_surface = pygame.display.get_surface() 
        self.save_system = SaveSystem()

        #sprite groups (allte players, trees etc)
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group() #keep a track which sprite is collidable
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        #create after the setup of the player
        self.overlay = Overlay(self.player, self.display_surface)
        self.transition = Transition(self.reset, self.player)

        #sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining #add to the level itself
        self.sky = Sky()

        #shop
        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        #music
        self.success = pygame.mixer.Sound('audio/success.wav')
        self.success.set_volume(0.3)
        #self.music = pygame.mixer.Sound('audio/music.mp3')
        #self.music.play(loops = -1)
    
    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        # Reset tree sprites to ensure correct initialization
        self.tree_sprites.empty()  # Clear any previous tree sprites

        #house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y* TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y* TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        #fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y* TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        #water
        water_frames = import_folder('graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites, LAYERS['water'])

        # Inside Level.setup():
        for obj in tmx_data.get_layer_by_name('Objects'):
            if obj.name == 'Giraffe':
                print(f"[DEBUG] Adding Giraffe at ({obj.x}, {obj.y})")
                Giraffe(pos=(obj.x, obj.y), group=self.all_sprites)

        for obj in tmx_data.get_layer_by_name('Objects'):
            if obj.name == 'Chicken':
                print(f"[DEBUG] Adding Chicken at ({obj.x}, {obj.y})")
                Chicken(pos=(obj.x, obj.y), group=self.all_sprites)

        # Trees
        #print("[DEBUG] Starting tree creation from TMX layer 'Trees'")
        for obj in tmx_data.get_layer_by_name('Trees'):
            #print(f"[DEBUG] Processing object at ({obj.x}, {obj.y}), name: {getattr(obj, 'name', 'Unnamed Object')}")
            if hasattr(obj, 'name') and obj.name in ['Small', 'Large']:  # Match against valid tree names
                Tree(
                    (obj.x, obj.y),
                    obj.image,
                    [self.all_sprites, self.collision_sprites, self.tree_sprites],
                    obj.name,
                    self.all_sprites,
                    self.player_add
                )
                '''print(f"[DEBUG] Added Tree: {obj.name} at ({obj.x}, {obj.y})")
            else:
                print(f"[WARNING] Skipping non-tree object: {getattr(obj, 'name', 'Unnamed Object')} at ({obj.x}, {obj.y})")

        print(f"[DEBUG] Total trees added: {len(self.tree_sprites)}")'''

        # Cows
        for obj in tmx_data.get_layer_by_name('Objects'):
            if obj.name == 'Cows':
                print(f"[DEBUG] Adding Cow at ({obj.x}, {obj.y})")
                cow_image = pygame.image.load('graphics/objects/Free Cow Sprites.png').convert_alpha()
                cow_image = pygame.transform.scale(cow_image, (64, 64))  # Scale sprite to tile size
                Generic(
                    pos=(obj.x, obj.y),
                    surf=cow_image,
                    groups=self.all_sprites,
                    z=LAYERS['main']
                )

        # Load Fish and Object Layer
        for obj in tmx_data.get_layer_by_name('Objects'):
            if hasattr(obj, 'name') and obj.name in ['Starfish', 'Plastic Bag', 'Snail', 'Blue Fish', 'Orange Fish']:
                print(f"[DEBUG] Object Found: {obj.name} at ({obj.x}, {obj.y}) with size ({obj.width}, {obj.height})")

                if obj.image:  # Ensure the object has an image
                    object_image = pygame.transform.scale(
                        obj.image,
                        (int(obj.width), int(obj.height))
                    )
                    
                    Generic(
                        pos=(obj.x, obj.y),
                        surf=object_image,
                        groups=[self.all_sprites, self.interaction_sprites],
                        z=LAYERS['Objects'],  # Ensure objects are above the ground layer
                        name=obj.name  # Ensure name is passed correctly
                    )
                #else:
                    #print(f"[ERROR] Object {obj.name} has no image associated with it!")

        #wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # Farmable Layer
        for x, y, surf in tmx_data.get_layer_by_name('Farmable').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['ground'])
        

        #collusions tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
        
        # Player 
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                # DEBUG: Print tree_sprites before passing to Player
                #print("tree_sprites in Level setup:", self.tree_sprites)
                self.player = Player(
                    pos = (obj.x,obj.y), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop = self.toggle_shop,
                    level=self  # Pass the Level instance here)
                )
            if obj.name == 'Bed':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)
            
            if obj.name == 'Trader':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

        Generic(pos = (0, 0), 
                surf = pygame.image.load('graphics/world/ground.png').convert_alpha(),
                groups = self.all_sprites,
                z = LAYERS['ground'])

    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.success.play()

    def toggle_shop(self):

        self.shop_active = not self.shop_active #turn on or off

    def reset(self):

        #print("[DEBUG] Resetting day...")
        #print(f"Before Reset: Inventory: {self.player.item_inventory}, Seeds: {self.player.seed_inventory}, Money: {self.player.money}")

        #plants
        self.soil_layer.update_plants()

        #Soil
        self.soil_layer.remove_water()
        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        #apples on trees
        for tree in self.tree_sprites.sprites():
            if isinstance(tree, Tree):  # Ensure the object is an instance of Tree
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
            tree.create_fruit()
        #print(f"After Reset: Inventory: {self.player.item_inventory}, Seeds: {self.player.seed_inventory}, Money: {self.player.money}")

        '''else:
            print(f"Skipping non-tree objects")  # Print the type of the object'''

        #sky
        self.sky.start_color = [255,255,255]

        """Save day progress before resetting the day."""
        self.save_system.record_day(
            day=self.save_system.data["current_day"],
            inventory=self.player.item_inventory,
            seed_inventory=self.player.seed_inventory,
            money=self.player.money
        )
        #print(f"[DEBUG] Day {self.save_system.data['current_day']} saved.")
        #print(f"Day {self.save_system.data['current_day']} progress saved!")

    def run(self, dt):

        #drawing logic
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        #updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)

        if self.player.sleep:
            self.transition.play()

        #Weather
        self.overlay.display()

        #rain
        if self.raining and not self.shop_active:
            self.rain.update()
        
        #daytime
        self.sky.display(dt)

        # Display Time of Day
        time_of_day = self.sky.get_time_of_day()
        font = pygame.font.SysFont('Comic Sans MS', 20)
        time_text = font.render(f"Time of Day: {time_of_day}", True, (255, 255, 255))
        # Calculate the position on the far right
        text_rect = time_text.get_rect()
        text_rect.topright = (SCREEN_WIDTH - 10, 10)  # 10px padding from the right and top

        self.display_surface.blit(time_text, text_rect)

        pygame.display.update()
        #print(self.player.item_inventory)

        #if self.player.sleep:
            #self.transition.play()
        
        

class CameraGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # Calculate the offset based on the player's position
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # Loop through all layers and draw sprites in those layers
        for layer_name, layer_value in sorted(LAYERS.items(), key=lambda x: x[1]):  # Sort layers by value
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):  # Sort sprites by their z value
                if sprite.z == layer_value:
                    # Apply the camera offset
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
                    '''if isinstance(sprite, Tree):
                        print(f"[DEBUG] Drawing Tree at {sprite.rect.topleft} on layer {layer_name}")'''