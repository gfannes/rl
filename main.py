import simu
import torch
import torch.nn as nn
import torch.optim as optim
import random
import math

class LeftRight:
	def __init__(self):
		self.prev_action = 1
	def action(self, obs):
		self.prev_action = 1-self.prev_action
		return self.prev_action

class Net(nn.Module):
	def __init__(self, obs_size, hidden_size):
		super(Net, self).__init__()
		self.net = nn.Sequential(
			nn.Linear(obs_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, hidden_size),
			nn.Tanh(),
			nn.Linear(hidden_size, 1),
			nn.Sigmoid()
			)
	def forward(self, obs_v):
		return self.net(obs_v)
	def prob(self, obs):
		return self.forward(torch.FloatTensor(obs)).data.numpy()[0]
	def action(self, obs):
		return 1 if random.random() <= self.prob(obs) else 0

class Episode:
	def __init__(self, start_segment_ix):
		self.start_segment_ix = start_segment_ix
		self.steps = []
		self.reward = 0.0
	def __repr__(self):
		return f"{self.start_segment_ix}~{self.reward}"
	def append(self, obs, action, reward):
		self.steps.append((obs, action, reward))
		self.reward += reward
	def create(env, policy, start_segment_ix = None, max_steps = 100):
		obs = env.reset(start_segment_ix)
		episode = Episode(env.segment_ix)
		for i in range(max_steps):
			action = policy.action(obs)
			new_obs, reward, is_done, _ = env.step(action)
			if is_done:
				break
			episode.append(obs, action, reward)
			obs = new_obs
		return episode

beam_count = 10
env = simu.Env(beam_count)

policy = LeftRight()

hidden_size = 10
policy = Net(beam_count, hidden_size)
objective = nn.MSELoss()
optimizer = optim.Adam(params=policy.parameters(), lr = 0.01)

def create_steps(n, fraction_to_keep, env, policy, start_segment_ix = None):
	start_segment_ix__episodes = {}
	for i in range(n):
		episode = Episode.create(env, policy, start_segment_ix)
		start_segment_ix__episodes.setdefault(episode.start_segment_ix, []).append(episode)
	def by_reward(episode):
		return episode.reward
	for episodes in start_segment_ix__episodes.values():
		episodes.sort(reverse=True, key=by_reward)
	best_steps = []
	for episodes in start_segment_ix__episodes.values():
		end = math.floor(len(episodes)*fraction_to_keep)
		best_episodes = episodes[0:end]
		for episode in best_episodes:
			best_steps.extend(episode.steps)
	return best_steps

for i in range(100):
	print(i)
	steps = create_steps(100, 0.3, env, policy, 0)
	print(sum(s[2] for s in steps), len(steps))
	optimizer.zero_grad()
	obs_v = torch.FloatTensor([s[0] for s in steps])
	# print(f"obs_v: {obs_v}")
	tgt_v = torch.FloatTensor([s[1] for s in steps])
	# print(f"tgt_v: {tgt_v}")
	act_v = policy(obs_v)
	act_v = torch.reshape(act_v, (act_v.size(dim=0),))
	# print(f"act_v: {act_v}")
	loss_v = objective(act_v, tgt_v)
	# print(loss_v)
	loss_v.backward()
	optimizer.step()
