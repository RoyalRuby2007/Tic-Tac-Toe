import random
from .base import Agent

class RandomAgent(Agent):
    name = "Random"
    def __init__(self, seed=None):
        super().__init__(); self.rng = random.Random(seed)
    def select_move(self, state):
        return self.rng.choice(state.legal_moves())