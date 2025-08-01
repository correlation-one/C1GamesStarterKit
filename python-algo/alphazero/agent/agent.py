import torch
import torch.nn as nn
import torch.nn.functional as F

class Agent(nn.Module):
    def __init__(self, policy, loss, mcts, optimizer, final_selection, epochs, device):
        self.device = torch.device(device)
        """do some more magic"""