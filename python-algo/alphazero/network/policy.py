import torch
import torch.nn as nn
import torch.nn.functional as F

class Policy(nn.Module):
    def __init__(self, representation_dim, action_dim, action_bound, hidden_dim, nonlinearity):
        super().__init__()
        self.representation_dim = representation_dim
        self.action_dim = action_dim
        self.action_bound = action_bound
        self.hidden_dim = hidden_dim
        self.nonlinearity = nonlinearity

        # do some magic
    def forward(self, x):
        # need to understand what we're returning here
        return x