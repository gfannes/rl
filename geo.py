import math

def norm(p):
	x, y = p
	return math.sqrt(x*x+y*y)

def normalize(v):
	n = norm(v)
	vx, vy = v
	return (vx/n, vy/n)

def direction(a, b):
	ax, ay = a
	bx, by = b
	return normalize((bx-ax, by-ay))

# From https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
def point_in_triangle(point, triangle):
    """Returns True if the point is inside the triangle
    and returns False if it falls outside.
    - The argument *point* is a tuple with two elements
    containing the X,Y coordinates respectively.
    - The argument *triangle* is a tuple with three elements each
    element consisting of a tuple of X,Y coordinates.

    It works like this:
    Walk clockwise or counterclockwise around the triangle
    and project the point onto the segment we are crossing
    by using the dot product.
    Finally, check that the vector created is on the same side
    for each of the triangle's segments.
    """
    # Unpack arguments
    x, y = point
    ax, ay = triangle[0]
    bx, by = triangle[1]
    cx, cy = triangle[2]
    # Segment A to B
    side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
    # Segment B to C
    side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
    # Segment C to A
    side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)
    # All the signs must be positive or all negative
    return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)

# From https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
def intersection(a, b, c, d):
	ax, ay = a
	bx, by = b
	cx, cy = c
	dx, dy = d

	denom = (ax-bx)*(cy-dy) - (ay-by)*(cx-dx)

	f1, f2 = (ax*by-ay*bx), (cx*dy-cy*dx)

	px = f1*(cx-dx) - (ax-bx)*f2
	py = f1*(cy-dy) - (ay-by)*f2

	return (px/denom, py/denom)

def add(a, b, f = 1.0):
	ax, ay = a
	bx, by = b
	return (ax+f*bx, ay+f*by)

def diff(a, b):
	ax, ay = a
	bx, by = b
	return (ax-bx, ay-by)

def distance(a, b):
	return norm(diff(a, b))

# abcd is a ccw quadrilateral
def intersection_edge(point, direction, a, b, c, d):
	pa = diff(a, point)
	pb = diff(b, point)
	pc = diff(c, point)
	pd = diff(d, point)
	da = determinant(pa, direction)
	db = determinant(pb, direction)
	dc = determinant(pc, direction)
	dd = determinant(pd, direction)
	if da >= 0 and db < 0:
		return 0
	if db >= 0 and dc < 0:
		return 1
	if dc >= 0 and dd < 0:
		return 2
	return 3

def determinant(a, b):
	ax, ay = a
	bx, by = b
	return ax*by - ay*bx