# import gym
# import chess_gym
# # import gym_chess
# # print(gym.envs.registry)
# # env_dict = gym.registry.env_specs.copy()

# env = gym.make("Chess-v0")
# env.reset()
# print(env.render(mode="unicode"))

# # for env in env_dict:
# #     if 'Chess-v0' in env:
# #         print("Remove {} from registry".format(env))
# #         del gym.envs.registry.env_specs[env]

# def run():
#     terminal = False
#     while not terminal:
#         action = env.action_space.sample()
#         observation, reward, terminal, info = env.step(action)
#         # info returns a dictionary
#         """
#             {
#                 turn (side to move on),
#                 castling_rights (bitmask w rooks for castling),
#                 fullmove_number (counts move pairs),
#                 halfmove_clock (half-moves since last capture/pawn move),
#                 promoted,
#                 ep_square (potential en passant square on third/sixth rank, otherwise returns None)
#             }
#         """
#         env.render()

#     env.close()

# if __name__ == "__main__":
#     run()

import gym
import chess_gym
import cairo

env = gym.make("Chess-v0")
env.reset()

terminal = False

while not terminal:
  action = env.action_space.sample()
  observation, reward, terminal, info = env.step(action)
  env.render()
  
env.close()