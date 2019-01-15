from collections import deque
from tensorflow import keras
from params import *
import numpy as np 
import random
class Agent():
    def __init__(self,
            hl_size=[10,10],
            state_size=OBSERVATIONS*2-1, #All states plus the gradients
            action_size=VALVE_POSITIONS
        ):

        self.state_size = state_size
        self.action_size = action_size
        self.action_choices = self.get_action_choices(action_size)
        self.memory = deque(maxlen=2000)
        self.gamma = GAMMA    # discount rate
        self.epsilon = EPSILON  # exploration rate
        self.epsilon_min = EPSILON_MIN
        self.epsilon_decay = EPSILON_DECAY
        self.learning_rate = LEARNING_RATE

        self.memory = deque(maxlen=2000) 
        self.ANN_model = self.build_ANN(state_size,hl_size,action_size,learning_rate=0.01)
        
    
    def build_ANN(self,state_size,hl_size,action_size,learning_rate):    
        # Defining network model
        model = keras.Sequential()
        model.add(keras.layers.Dense(hl_size[0],input_shape=(state_size,),activation='relu'))
        for i in hl_size:
            model.add(keras.layers.Dense(i,activation='relu'))
        model.add(keras.layers.Dense(action_size,activation='softmax'))
        
        model.compile(
            loss='mse',
            optimizer=keras.optimizers.Adam(lr=learning_rate)
            )
        return model

    def get_action_choices(self,action_size):
        valve_positions= []
        for i in range(action_size):
            valve_positions.append(i/(action_size-1))
        return np.array(valve_positions)
        

    def remember(self, state, action, next_state,reward,done):
        self.memory.append((state, action, next_state, reward,done))

    def act_greedy(self,states):
        states_data = self.process_state_data(states)
        pred = self.ANN_model.predict(states_data) 
        choice = np.where(pred[0]==max(pred[0]))[0][0]
        return choice
         
    def process_state_data(self,states):
        states_grad = [states[i+1]- states[i] for i in range(len(states[:-1]))] # calculate dhdt
        states_data = np.array(states+states_grad) # Combine level with gradient of level
        states_data = states_data.reshape(1,len(states_data))
        return states_data

    def act(self, states):
        if np.random.rand() <= self.epsilon: # Exploration 
            random_action = random.randint(0,self.action_size-1)
            return random_action
        return self.act_greedy(states)
        
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, next_state,reward,done in minibatch:
            target = reward
            state_data = self.process_state_data(state)
            next_state_data = self.process_state_data(next_state)
            if not done:
                target = (reward + self.gamma *np.amax(self.ANN_model.predict(next_state_data)))
            target_f = self.ANN_model.predict(state_data)
            target_f[0][action] = target
            self.ANN_model.fit(state_data, target_f, epochs=1, verbose=0)
    def decay_exploration(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay