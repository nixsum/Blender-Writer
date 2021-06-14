import numpy as np
from math import sqrt
from vector import Point as P
from vector import Vector as V

import os
import cv2





class Sheet:

	def __init__(self, origin, width, height, r_write=0.04, density=100, fps=30):
		# Set origin and size
		self.origin = P.from_list(origin)

		self.width = width
		self.height = height

		self.width_p = int(width * density)
		self.height_p = int(height * density)

		# Write variables
		self.r_write = r_write
		self.r_check = int(r_write * density)
		self.a_pixel = 1 / density

		# Create pixel array
		self.pixels = np.zeros((self.width_p, self.height_p, 3), dtype=np.uint8)
		self.pixels.fill(255)

		path = os.path.join(os.path.join(os.getcwd(), 'sheet'), 'video.avi')

		fourcc = cv2.VideoWriter_fourcc(*'DIVX')
		self.video = cv2.VideoWriter(path, fourcc, fps, (self.width_p, self.height_p))



	def _vector_on_sheet(self, point_in_world):
		v = V.from_points(self.origin, point_in_world)
		v.y = -v.y
		v.x /= self.width
		v.y /= self.height
		return v

	def _indeces_on_sheet(self, point_in_world):
		v = self._vector_on_sheet(point_in_world)
		x = int(v.x * self.width_p)
		y = int(v.y * self.height_p)
		return x, y


	def _set(self, x, y, value):
		self.pixels[x, y][0] = value
		self.pixels[x, y][1] = value
		self.pixels[x, y][2] = value



	def write(self, writer_point):
		writer_indeces = self._indeces_on_sheet(writer_point)
		writer_vector = V(writer_point.x, writer_point.y, writer_point.z)

		for x in range(-self.r_check, self.r_check + 1):
			for y in range(-self.r_check, self.r_check + 1):

				if writer_indeces[0] + x >= 0 and writer_indeces[0] + x < self.width_p and writer_indeces[1] + y >= 0 and writer_indeces[1] + y < self.height_p:

					check_vector = V(writer_vector.x + x*self.a_pixel, writer_vector.y + y*self.a_pixel, self.origin.z)
					
					if writer_vector.eucledian(check_vector) <= self.r_write:
						self._set(writer_indeces[0] + x, writer_indeces[1] + y, 0)

		


	def add_frame(self):
		pixels = np.swapaxes(self.pixels, 0, 1)
		self.video.write(pixels)


	def export(self):
		self.video.release()

