import pygame
from settings import *
from support import * 
from timer1 import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.import_assets()
        self.status = 'down'
        self.frame_index = 0 

        #general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        #movement attributes 
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        #timers
        self.timers = {
            'tool_use': Timer(350,self.use_tool),
            'tool switch': Timer(200)
        }

        #Tools usage
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0 
        self.selected_tool = self.tools[self.tool_index]

    def use_tool(self):

        print(self.selected_tool)

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe':[],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}
        
        for animation in self.animations.keys():
            full_path = 'graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
        #print(self.animations)
    
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool_use'].active:
            #directions
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
                
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            
            #tool usage
            if keys[pygame.K_SPACE]:
                #if condition is true - run timer for tool use - If player uses tool then add the status to the action
                self.timers['tool_use'].activate()
                #if player is moving to right  - player will keep moving to right when using tool, its not allowed to use any input
                self.direction = pygame.math.Vector2()
                self.frame_index = 0 

            #change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                #if tool index > length of tools  => tool index to 0
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0 
                self.selected_tool = self.tools[self.tool_index]

    def get_status(self):
        #if the player is not moving (idle):
        if self.direction.magnitude() == 0:
            #add _idle to the status (manipulate string to get status with idle)
            self.status = self.status.split('_')[0] + '_idle'

        #tool use 
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def move(self,dt):

        #normalizing a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        #Horizontal Movement 
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        #Vertical Movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)