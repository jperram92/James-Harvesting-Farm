import pygame
from settings import *

class Overlay:
    def __init__(self,player):        
        #general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # Use self to reference instance variables
        overlay_path = 'graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):
        #tools
        tool_surf = self.tools_surf[self.player.selected_tool]
        self.display_surface.blit(tool_surf,(0,0))
        #seed
        #seed_surf = self.seeds_surf[self.player.selected_seed]