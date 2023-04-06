import torch 
import random
import numpy as np
from Snake_game import Direction,Point,SnakeGameAI,BLOCK_SIZE
from collections import deque
from Model import LinearQNet, QTrainer
from Helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.002
SNAKE_VIEW_DISTANCE = 3

class Agent:


    def __init__(self):
        self.numberOfGames = 0
        self.epsilon = 0.1
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = LinearQNet(12+7*SNAKE_VIEW_DISTANCE, 600, 3)
        self.trainer = QTrainer(self.model, learningRate=LEARNING_RATE, gamma=self.gamma)

    def getState(self, game):

        head = game.snake[0]

        
        
        dirL = game.direction == Direction.LEFT
        dirR = game.direction == Direction.RIGHT
        dirU = game.direction == Direction.UP
        dirD = game.direction == Direction.DOWN

        state = [
            dirL,
            dirR,
            dirU,
            dirD,
            
             
            game.food.x < game.head.x,  
            game.food.x > game.head.x,  
            game.food.y < game.head.y,  
            game.food.y > game.head.y,  

            game.snake[-1].x < game.head.x,
            game.snake[-1].y < game.head.y,
            game.snake[-1].x > game.head.x,
            game.snake[-1].y > game.head.y,
         
            ]
        
        for distance in range(1, SNAKE_VIEW_DISTANCE + 1):
            pointL = Point(head.x - BLOCK_SIZE*distance, head.y)
            pointR = Point(head.x + BLOCK_SIZE*distance, head.y)
            pointU = Point(head.x, head.y - BLOCK_SIZE*distance)
            pointD = Point(head.x, head.y + BLOCK_SIZE*distance)
            pointLU = Point(head.x - BLOCK_SIZE*distance, head.y - BLOCK_SIZE*distance)
            pointRU = Point(head.x + BLOCK_SIZE*distance, head.y - BLOCK_SIZE*distance)
            pointLD = Point(head.x - BLOCK_SIZE*distance, head.y + BLOCK_SIZE*distance)
            pointRD = Point(head.x + BLOCK_SIZE*distance, head.y + BLOCK_SIZE*distance)


            rightCheck = (dirR and game.isCollision(pointR)) or  (dirL and game.isCollision(pointL)) or (dirU and game.isCollision(pointU)) or (dirD and game.isCollision(pointD))
            upCheck = (dirU and game.isCollision(pointR)) or (dirD and game.isCollision(pointL)) or (dirL and game.isCollision(pointU)) or (dirR and game.isCollision(pointD))
            leftCheck =  (dirD and game.isCollision(pointR)) or (dirU and game.isCollision(pointL)) or (dirR and game.isCollision(pointU)) or (dirL and game.isCollision(pointD))
            diagonalLUCheck = game.isCollision(pointLU)
            diagonalRUCheck = game.isCollision(pointRU)
            diagonalLDCheck = game.isCollision(pointLD)
            diagonalRDCheck = game.isCollision(pointRD)


            state.append(rightCheck)
            state.append(upCheck)
            state.append(leftCheck)
            state.append(diagonalLUCheck)
            state.append(diagonalRUCheck)
            state.append(diagonalLDCheck)
            state.append(diagonalRDCheck)

        

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, nextState, done):
        self.memory.append((state, action, reward, nextState, done))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            miniSample = random.sample(self.memory, BATCH_SIZE)
        else:
            miniSample = self.memory

        states, actions, rewards, nextStates, dones = zip(*miniSample)
        self.trainer.trainStep(states, actions, rewards, nextStates, dones)

    def trainShortMemory(self, state, action, reward, nextState, done):
        self.trainer.trainStep(state, action, reward, nextState, done)

    def getAction(self, state):
        breakthroughPoint = 80
        self.epsilon = breakthroughPoint - self.numberOfGames
        finalMove = [0,0,0]
        if random.randint(0,2*breakthroughPoint) < self.epsilon:
            move = random.randint(0,2)
            finalMove[move] = 1
        else:
             state0 = torch.tensor(state, dtype = torch.float)
             prediction = self.model(state0)
             move = torch.argmax(prediction).item()
             finalMove[move] = 1

        return finalMove

def train():
    plotScores = []
    plotMeanScores = []
    totalScore = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        stateOld = agent.getState(game)

        finalMove = agent.getAction(stateOld)

        reward, done, score = game.playStep(finalMove)
        stateNew = agent.getState(game)

        agent.trainShortMemory(stateOld, finalMove, reward, stateNew, done)

        agent.remember(stateOld, finalMove, reward, stateNew, done)

        if done:
            game.reset()
            agent.numberOfGames +=1
            agent.trainLongMemory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.numberOfGames, "Score", score, "Record", record)

            plotScores.append(score)
            totalScore += score
            meanScore = totalScore / agent.numberOfGames
            plotMeanScores.append(meanScore)
            plot(plotScores, plotMeanScores)

            

if __name__ == '__main__':
    train()