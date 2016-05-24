import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        # sets self.env = env, state = None, next_waypoint = None, and a default color
        super(LearningAgent, self).__init__(env)
        self.color = 'red'  # override color
        # simple route planner to get next_waypoint
        self.planner = RoutePlanner(self.env, self)
        # TODO: Initialize any additional variables here

        # Possible actions
        #statistics
        self.total = 0
        self.success = 0
        self.reward_Total = 0 
        actions = self.env.valid_actions
        # Traffic light state choices
        traffic_light = ['red', 'green']
        # Next_waypoint oncoming states have the same choices
        next_point, oncoming = actions, actions

        # Initialize the Q-values
        self.Q_table = {}
        for light in traffic_light:
            for point in next_point:
                for come in oncoming:
                    self.Q_table[(light, point, come)] = \
                        {None: 0, 'forward': 0, 'left': 0, 'right': 0}

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        # from route planner, also displayed by simulator 
        self.next_waypoint = self.planner.next_waypoint()
        # TODO: Update state
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        self.state = (inputs['light'], self.next_waypoint, inputs['oncoming'])

        print '-------'
        print 'Self State : ', self.state
        print 'Deadline : ', deadline
        print 'Next_waypoint : ', self.next_waypoint
        # TODO: Select action according to your policy

        # random action each ~7 steps think how to varies this with learning
        M_Q = self.Q_table[self.state]
        
        epsilon = 0.9/(1+  self.total)
        gamma = 0.7
        alpha = 0.3
        r = random.random()
        
        if epsilon > r:
            # Exploration
            action = random.choice([None, 'forward', 'left', 'right'])
        else:
           
            if all(value == 0 for value in M_Q.values()):
                # if all values are == 0 choose random direction,
                # action = random.choice([None, 'forward', 'left', 'right'])
                # But a better stratagy will be to use the direction learned when no one was on the cross road 
                M_Q_t= self.Q_table[ (self.state [0], self.state [1] , None)]
                action =  max(M_Q_t, key=M_Q_t.get)
            else:
                # Exploitation
                # else choose max Q
                action = max(M_Q, key=M_Q.get)

        # Execute action and get reward
        print 'Action :', action
        reward = self.env.act(self, action)
        print 'Reward : ', reward
        # Statistics
        add_total = False
        if deadline == 0:
            add_total = True
        if reward > 5:
            self.success += 1
            add_total = True
        if add_total:
            self.total += 1
            print("success: {} / {}".format(self.success, self.total))
        self.reward_Total+=reward
        
        # sense the new position
        # from route planner, also displayed by simulator
        Next_waypoint_new = self.planner.next_waypoint()
        inputs_new = self.env.sense(self)
        deadline_new = self.env.get_deadline(self)

        state_new = (inputs_new['light'], Next_waypoint_new, inputs_new['oncoming'])

        # TODO: Update state

        print '-------'
        # TODO: Update state

        # TODO: Learn policy based on state, action, reward
        # Set the tuning parameters

       #  print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


        self.Q_table[self.state][action] = \
            (1-alpha) * (self.Q_table[self.state][action]) + \
            alpha * (reward + gamma * max(self.Q_table[state_new].values()))
        if self.total==20:    
            print self.reward_Total

        if self.total==100:
            print self.reward_Total
            print self.Q_table
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    # reduce update_delay to speed up simulation
    sim = Simulator(e, update_delay=0.0001)
    sim.run(n_trials=20)  # press Esc or close pygame window to quit
   

if __name__ == '__main__':
    run()
