from models.tank_model.tank import Tank
from visualize.window import Window
import numpy as np 
import matplotlib.pyplot as plt 
import random
import pygame
import sys
from drawnow import drawnow
#=============== PARAMETERS ==================#

# Model parameters
TANK_HEIGHT=10
TANK_RADIUS=2
TBCC = 10 # Time before choke change
DELAY=0
ADD_INFLOW = False

# Training parameters
MAX_TIME = 1000

# Render parameters
WINDOW_HEIGHT=350
WINDOW_WIDTH=500
RENDER=True
LIVE_REWARD_PLOT= True

EPISODES = 100
# ============ MAIN ===========================#
def main():

    # Get empty variables 
    tank = Tank(TANK_HEIGHT,TANK_RADIUS) # get model
    time_history = range(MAX_TIME) # Time range for episodes
    
    rewards = [] 

    # ============== RENDER========== #
    if RENDER:
        window = Window(tank,WINDOW_WIDTH,WINDOW_HEIGHT)

    
    # Live plotting of rewards
    if LIVE_REWARD_PLOT:
        plt.ion()  # enable interactivity
        fig = plt.figure(num="Max reward: {}".format(MAX_TIME))  # make a figure
        def plot_rewards():
            plt.plot(rewards,label="Episode number: {}".format(e))
            plt.legend()

    
    # Running episodes
    for e in range(EPISODES):
        tank.reset() # Reset level in tank
        level_history = DELAY*[tank.l] 
        valve_history = []
        
        # Add random choke openings with TBCC
        counter = 0
        while counter < MAX_TIME:
            valve_history.extend(TBCC*[np.random.uniform(0,1)])
            counter +=TBCC
        valve_history = np.array(valve_history).reshape(-1)
        
        # Running state in the episode
        for t in range(MAX_TIME):
            input_z = valve_history[t] # Addind indented choke position

            # Do action
            level_history.append(tank.l)
            
            # Enviroments response
            tank.change_level(z=input_z)

            # Add disturbance to tank
            if ADD_INFLOW:
                pass

            # Check terminate state
            if tank.l < tank.min or tank.l > tank.max:
                break
            
            # render tank
            if RENDER:
                running = window.Draw(input_z)
                if not running:
                    break
        rewards.append(t)
        
        # Live plot rewards
        if LIVE_REWARD_PLOT:
            drawnow(plot_rewards)

        
    pygame.display.quit()
    print("\nMean rewards for episodes: ", np.mean(rewards)) 
    print("Rewards for the last episode: ", rewards[-1])

if __name__ == "__main__":
    main()