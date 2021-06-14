import vectors
import math


class Vector(vectors.Vector):

	def __init__(self, *args):
		vectors.Vector.__init__(self, *args)

	def new(self):
		return Vector(self.x, self.y, self.z)

	def to_tuple(self):
		return (self.x, self.y, self.z)

	def to_point(self):
		return Point(self.x, self.y, self.z)

	def sum(self, other):
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

	def subtract(self, other):
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

	def divide(self, n):
		return Vector(self.x / n, self.y / n, self.z / n)

	def hadamard(self, other):
		return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

	def eucledian(self, other):
		return math.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2) + pow(self.z - other.z, 2))







class Point(vectors.Point):

	def __init__(self, *args):
		vectors.Point.__init__(self, *args)

	def to_tuple(self):
		return (self.x, self.y, self.z)
