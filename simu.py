import random
import geo

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
	def distance_to_edge(self, point, direction):
		i = geo.intersection(self.start.left, self.start.right, point, geo.add(point, direction))

class Track:
	def __init__(self, lines):
		segments = []
		n = len(lines)
		for ix, line in enumerate(lines):
			segments.append(Segment(line, lines[(ix+1)%n]))
		self.segments = segments

	def random_state(self):
		segment = random.choice(self.segments)
		def interpolate(a, b, f):
			ax, ay = a
			bx, by = b
			return (ax+f*(bx-ax), ay+f*(by-ay))
		point_start = interpolate(segment.start.left, segment.start.right, random.uniform(0.1, 0.9))
		point_finish = interpolate(segment.finish.left, segment.finish.right, random.uniform(0.1, 0.9))
		position = interpolate(point_start, point_finish, random.uniform(0.1, 0.9))
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

	def segment(self, point):
		for segment in self.segments:
			if segment.inside(point):
				return segment

class Env:
	def __init__(self):
		self.track = Track.diamond()
		self.position, self.direction = None, None

	def reset(self):
		self.position, self.direction = self.track.random_state()
		segment = self.track.segment(self.position)
		assert segment, "A newly created position should be on the track"
		return segment.distance_to_edge(self.position, self.direction)