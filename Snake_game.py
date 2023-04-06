import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)



class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')


WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 10000
LAST_SPEED = 10000
STANDARD_SPEED =40

events = pygame.event.get()
for event in events:
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            SPEED -= 10
            print(SPEED)
        if event.key == pygame.K_RIGHT:
            SPEED += 10
            print(SPEED)

class SnakeGameAI:
    
    def __init__(self, w=800, h=600):
        self.w = w
        self.h = h
        
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

        
        self.speed = SPEED
        self.speed_increment = 120
        
     
    def reset(self):
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None
        self._placeFood()
        self.frameIteration =0
        
    def _placeFood(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._placeFood()
        
    def playStep(self, action):
    
        self.frameIteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Increase or decrease speed if right or left arrow key is pressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.speed -= self.speed_increment
                    self.LAST_SPEED = self.speed
                    print(f"Speed decreased: {self.speed}")
                elif event.key == pygame.K_RIGHT:
                    self.speed += self.speed_increment
                    self.LAST_SPEED = self.speed
                    print(f"Speed increased: {self.speed}")
                elif event.key == pygame.K_DOWN:
                    self.speed = STANDARD_SPEED
                elif event.key == pygame.K_UP:
                    self.speed = LAST_SPEED
                    
        self._move(action) 
        self.snake.insert(0, self.head)
        
        reward = 0
        gameOver = False
        if self.isCollision() or self.frameIteration > 100*len(self.snake):
            gameOver = True
            reward = -10
            return reward, gameOver, self.score
            
        if self.head == self.food:
            reward = 10
            self.score += 1
            self._placeFood()
        else:
            self.snake.pop()
        
    
        self._updateUI()
        self.clock.tick(self.speed)

        return reward, gameOver, self.score
        
    def isCollision(self, point=None):

        if point is None:
            point = self.head
        
        if point.x > self.w - BLOCK_SIZE or point.x < 0 or point.y > self.h - BLOCK_SIZE or point.y < 0:
            return True
        
        if self.head in self.snake[1:]:
            return True
        
        return False
        
    def _updateUI(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):

        #[straight, right, left]    
        clock_wise = [Direction.RIGHT, Direction.DOWN,Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
       
        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] 
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx +1) % 4
            new_dir = clock_wise[next_idx] 
        else:
            next_idx = (idx -1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir


        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
            

