
from threading import Timer, Thread
import time
from context import *
from clock import *
from baseaction import *

class Engine:
    """
    An engine drives a sequence of actions with a context
    """
    
    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return self.config['main']['name']

    def run(self, context=None):
        """
        """
        try:
            context = self.__run(context)
        except Exception as e:
            print("Exception:\n", e)
        finally:
            # Keep the context for the follower engines
            Clock.trigger_followers(Engine.run, self, context)

    def start(self):
        """
        """
        
        # TODO: Register Engine in clock.tick for very 30 s
        triggers = self.config['main']['triggers']
        if isinstance(triggers, str):
            triggers = [triggers]
        for trigger in triggers:
            Clock.register(self, trigger)   


    def __run(self, context):
        """
        """
        if 'action' not in self.config:
            return
        actions_config = self.config['action']
        if 'main' not in actions_config:
            print("Counld NOT find main action!")
        else:
            print('Engine', self.config['main']['name'])

        if not context:
            print('Create new context')
            context = Context()
        actions = self.load_actions(actions_config)

        for action in actions:
            if not action:
                raise Exception("No action loaded")
            self.run_action(action, context)
        return context

    def create_action(self, action_config):
        action_type = action_config['type']
        clz = Action.get_action_class(action_type)
        action = clz()
        action.set_action_config(action_config)
        return action

    def load_actions(self, actions_config):
        """
        Action.main would be the first action
        """
        actions = []

        action_config = actions_config['main']
        while action_config:
            action = self.create_action(action_config)
            actions.append(action)
            
            if 'next' not in action_config or action_config['next'] == '':
                break
            next_action = action_config['next']
            if next_action not in actions_config:
                raise Exception("No action provided")
            
            action_config = actions_config[next_action]

        return actions

    def run_action(self, action, context):
        """
        """
        # TODO: Log
        print("-" * 40)
        action.execute(context)

        

        
        