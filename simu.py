import random
import geo
import math

class Line:
	def __init__(self, left, right):
		self.left, self.right = left, right

class Segment:
	def __init__(self, start, finish):
		self.start, self.finish = start, finish
	def inside(self, point):
		# TODO: optimize with direct check iso splitting in 2 triangles
		inside_trianle_1 = geo.point_in_triangle(point, [self.start.left, self.finish.right, self.start.right])
		inside_trianle_2 = geo.point_in_triangle(point, [self.start.left, self.finish.right, self.finish.left])
		return inside_trianle_1 or inside_trianle_2
	def intersection(self, point, direction):
		i = geo.intersection_edge(point, direction, self.start.left, self.start.right, self.finish.right, self.finish.left)
		if i == 0:
			return geo.intersection(point, geo.add(point, direction), self.start.left, self.start.right), 'start'
		if i == 1:
			return geo.intersection(point, geo.add(point, direction), self.start.right, self.finish.right), 'right'
		if i == 2:
			return geo.intersection(point, geo.add(point, direction), self.finish.left, self.finish.right), 'finish'
		if i == 3:
			return geo.intersection(point, geo.add(point, direction), self.finish.left, self.start.left), 'left'

class Track:
	def __init__(self, lines):
		n = len(lines)
		self.segments = [Segment(line, lines[(ix+1)%n]) for ix, line in enumerate(lines)]
	def segment_count(self):
		return len(self.segments)
	def random_state(self, start_segment_ix = None):
		segment_cnt = self.segment_count()
		start_segment_ix = random.randrange(segment_cnt) if start_segment_ix is None else start_segment_ix%segment_cnt
		segment = self.segments[start_segment_ix]
		def interpolate(a, b, f):
			ax, ay = a
			bx, by = b
			return (ax+f*(bx-ax), ay+f*(by-ay))
		d = 0.1
		point_start = interpolate(segment.start.left, segment.start.right, random.uniform(d, 1.0-d))
		point_finish = interpolate(segment.finish.left, segment.finish.right, random.uniform(d, 1.0-d))
		position = interpolate(point_start, point_finish, random.uniform(0.0, d))
		direction = geo.direction(position, point_finish)
		return position, direction
	def diamond():
		d = 1.0
		lines = [ Line((d, 0), (2*d, 0)),
		Line((0, d), (0, 2*d)),
		Line((-d, 0), (-2*d, 0)),
		Line((0, -d), (0, -2*d)),
		]
		return Track(lines)
	def next_segment_ix(self, ix):
		return (ix+1)%self.segment_count()
	def segment_ix(self, point):
		for ix, segment in enumerate(self.segments):
			if segment.inside(point):
				return ix
	def ix__segment_(self, ix):
		return self.segments[ix%self.segment_count()]
	def distance_to_edge(self, point, direction, segment_ix = None):
		if segment_ix is None:
			segment_ix = self.segment_ix(point)
		if segment_ix is not None:
			segment = self.ix__segment_(segment_ix)
			edge_point, edge_type = segment.intersection(point, direction)
			while edge_type != 'left' and edge_type != 'right':
				segment_ix += 1 if edge_type == 'finish' else -1
				segment = self.ix__segment_(segment_ix)
				edge_point, edge_type = segment.intersection(point, direction)
			return geo.distance(point, edge_point)

class Env:
	def __init__(self, beam_count, speed = 0.1):
		self.track = Track.diamond()
		self.position, self.direction = None, None
		self.segment_ix, self.observation, self.reward = None, None, None
		angles = [(i*math.tau)/beam_count for i in range(beam_count)]
		self.beam_rotations = [((math.cos(angle), -math.sin(angle)), (math.sin(angle), math.cos(angle))) for angle in angles]
		self.speed = speed
	def get_observation(self):
		return self.observation
	def get_actions(self):
		return [0, 1]
	def reset(self, segment_ix = None):
		self.position, self.direction = self.track.random_state(segment_ix)
		self.on_changed_state_()
		return self.get_observation()
	def step(self, action):
		self.update_direction_and_position_(action)
		self.on_changed_state_()
		obs = self.get_observation()
		return obs, self.reward, obs is None, None
	def radar_beams_(self):
		dx, dy = self.direction
		return [(dx*r[0][0] + dy*r[0][1], dx*r[1][0] + dy*r[1][1]) for r in self.beam_rotations]
	def update_direction_and_position_(self, action):
		d, eps = 0.5, 0.05
		angle = random.uniform(d-eps, d+eps) if action == 0 else random.uniform(-d-eps, -d+eps)
		cos, sin = math.cos(angle), math.sin(angle)
		dx, dy = self.direction
		new_dir = (dx*cos-dy*sin, dx*sin+dy*cos)
		self.direction = geo.normalize(new_dir)
		self.position = geo.add(self.position, self.direction, self.speed)
	def on_changed_state_(self):
		new_segment_ix = self.track.segment_ix(self.position)
		if new_segment_ix is None:
			self.observation = None
			self.segment_ix = None
			self.reward = None
		else:
			if self.segment_ix is None or new_segment_ix == self.segment_ix:
				self.reward = 0.0
			elif new_segment_ix == self.track.next_segment_ix(self.segment_ix):
				self.reward = 1.0
			else:
				self.reward = -1.0
			self.segment_ix = new_segment_ix
			self.observation = [self.track.distance_to_edge(self.position, beam, new_segment_ix) for beam in self.radar_beams_()]
