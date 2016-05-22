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
        self.reward_Total= 0 
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
        Next_waypoint = self.planner.next_waypoint()
        # TODO: Update state
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        self.state = (inputs['light'], Next_waypoint, inputs['oncoming'])

        print '-------'
        print 'Self State : ' , self.state
        print 'Deadline : ', deadline
        print 'Next_waypoint : ', Next_waypoint
        # TODO: Select action according to your policy

        # random action each ~7 steps think how to varies this with learning
        M_Q = self.Q_table[self.state]
        if random.choice(['False', 'True', 'False', 'False', 'False', 'False', 'False'])=='True':
            action = random.choice([None, 'forward', 'left', 'right'])
        else:
            # if all values are == 0 choose Next_waypoint
            if all(value == 0 for value in M_Q.values()):
                action = Next_waypoint
            else:
                # else choose max Q
                action = max(M_Q, key=M_Q.get)

        # Execute action and get reward
        print 'Action :' , action
        reward = self.env.act(self, action)
        self.reward_Total+=reward
        print 'Reward : ', reward
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
        gamma = 0.1
        alpha = 0.5

        self.Q_table[self.state][action] = \
            (1-alpha) * (self.Q_table[self.state][action]) + \
            alpha * (reward + gamma * max(self.Q_table[state_new].values()))
        print self.reward_Total

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    # reduce update_delay to speed up simulation
    sim = Simulator(e, update_delay=0.001)
    sim.run(n_trials=10)  # press Esc or close pygame window to quit
   

if __name__ == '__main__':
    run()
