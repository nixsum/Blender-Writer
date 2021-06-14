import bpy
import math
import os

from sheet import Sheet
from vector import Vector as V, Point as P


CAMERA_POS = V(-3.6, -5.6, 3.8)

CANVAS_POS = V(-3.9, -1.9, 2.68)
CANVAS_ROTATION = V(0, 0, 0)
CANVAS_END_POS = CANVAS_POS.sum(V(-0.3, 0, 0.92))
CANVAS_END_ROTATION = V(0.47, 0, 0)



class Writer:

	def __init__(self, context, font, from_to, scale, height, step, r_write, r_write_min, res, starting_frame=1):
		self.pen = context['pen']
		self.pen_holder = context['pen holder']
		self.canvas = context['canvas']
		self.dipper = context['dipper']
		self.camera = context['camera']
		self.anchor = context['anchor']
		self.pen_exit = context['pen exit']
		
		# Clear animation data
		self.pen.animation_data_clear()
		self.pen_holder.animation_data_clear()
		self.canvas.animation_data_clear()
		self.dipper.animation_data_clear()
		self.camera.animation_data_clear()
		self.anchor.animation_data_clear()
		self.pen_exit.animation_data_clear()
		
		# font -> points of each character; from_to -> leftmost and rightmost point of each character
		self.font = font
		self.from_to = from_to

		self.scale = V.from_list(scale)
		self.distance_scale = V(0.5, 0.25, 0.1)
		self.step = step
		self.space = 0.1
		self.height = height
		self.dots_per_keyframe = 300
		
		# Sheet object
		sheet_origin = self.canvas.location
		sheet_width = self.canvas.dimensions[0]
		sheet_height = self.canvas.dimensions[1]
		self.sheet = Sheet(sheet_origin, sheet_width, sheet_height, r_write=r_write, density=res)
		self.r_write = r_write
		self.r_write_min = r_write_min

		# Offsets in time and self.space
		self.starting_frame = starting_frame
		self.frame_num = starting_frame
		self.delta = V.from_list(sheet_origin)
		self.delta.x += self.scale.x * 0.75
		self.delta.y -= self.scale.y * 1.5
		self.delta_og = self.delta.new()

		# Dipper
		self.count = 40

		# Camera
		self.camera_vector = V(-3.17045, -9.58766, 2.74916)

		# Set default positions
		self.add_keyframe(self.camera, CAMERA_POS.to_tuple(), starting_frame)
		self.add_keyframe(self.canvas, CANVAS_POS.to_tuple(), starting_frame)


	def get_space(self, char, char_next):
		current_rightmost = self.from_to[char][1]
		next_leftmost = self.from_to[char_next][0]
		if char_next in self.font.keys():
			return (current_rightmost - next_leftmost + self.space) * self.scale.x
		else:
			return 0


		
	

	def write_char(self, char, char_next, vector_last):
		# Create vector list
		keyframe_vectors = [V.from_list(pos) for pos in self.font[char]]

		# Add raised vector after and before character
		keyframe_vectors.insert(0, V(keyframe_vectors[0].x, keyframe_vectors[0].y, keyframe_vectors[0].z + 1.0))
		keyframe_vectors.append(V(keyframe_vectors[-1].x, keyframe_vectors[-1].y, keyframe_vectors[-1].z + 1.0))

		# Add keyframes
		self.add_keyframes_write(keyframe_vectors, vector_last)
		
		if char_next:
			self.delta.x += self.get_space(char, char_next)


		return keyframe_vectors[-1]


	def dip(self, vector_last, vector_next=None):
		dipper_vector = V.from_list(self.dipper.location)
		dipper_vector_raised = V.new(dipper_vector)
		dipper_vector_raised.z += 0.5
		dipper_vector.z += 0.15

		holder_offset = V(-1, -2, 0)

		self.add_keyframe_pen(dipper_vector_raised, self.frame_num + 50, holder_offset)
		self.add_keyframe_pen(dipper_vector, self.frame_num + 20, holder_offset)
		self.add_keyframe_pen(dipper_vector_raised, self.frame_num + 20, holder_offset)

		self.sheet.r_write = self.r_write

		return dipper_vector_raised


	def newline(self, step):
		d = int(step * (self.delta.x - self.delta_og.x) / self.canvas.dimensions.x)

		self.frame_num += d
		for _ in range(d):
			self.sheet.add_frame()

		self.delta.x = self.delta_og.x
		self.delta.y -= self.scale.y * (1 + self.height)

		
	
	def write(self, string):
		# Dipper count
		chars = 0

		# START
		starting_pos = V.from_list(self.pen_exit.location)
		vector_last = starting_pos.new()

		self.add_keyframe_pen(starting_pos, self.frame_num, move_z=True)
		self.dip(vector_last)

		# self.delta.x += (self.from_to[string[0]][0] + self.space) * self.scale.x
		######################

		# Split the string and calculate word length
		#### TODO 
		
		# Add keyframes
		for i in range(len(string)):

			if string[i] == '\n':
				self.newline(33)

			elif string[i] == ' ':
				self.delta.x += self.scale.x * 3/4
				for _ in range(10):
					self.sheet.add_frame()
					self.frame_num += 1

			else:
				if i+1 < len(string) and string[i+1] not in [' ', '\n']:
					vector_last = self.write_char(string[i], string[i+1], vector_last)
				else:
					vector_last = self.write_char(string[i], None, vector_last)


				if chars < self.count:
					self.sheet.r_write -= (self.r_write - self.r_write_min) / self.count


				chars += 1

				if chars >= self.count and i < len(string) - 1 and string[i+1] == ' ':
					vector_last = self.dip(vector_last).multiply(3)
					chars = 0
					

		# END
		# self.add_keyframe_pen(starting_pos, self.frame_num + 50, move_z=True)
		self.add_keyframe_pen(V.from_list(self.camera.location).sum(V(-3.0, 4.0, -1)), self.frame_num + 50, move_z=True)


		# OUTRO
		
		# Camera
		# self.add_keyframe(self.camera, CAMERA_POS.to_tuple(), self.frame_num - 40)
		# self.add_keyframe(self.camera, CAMERA_END_POS.to_tuple(), self.frame_num + 160)

		# Canvas
		self.add_keyframe(self.canvas, CANVAS_POS.to_tuple(), self.frame_num - 40, rotation=CANVAS_ROTATION.to_tuple())
		self.add_keyframe(self.canvas, CANVAS_END_POS.to_tuple(), self.frame_num + 160, rotation=CANVAS_END_ROTATION.to_tuple())


		self.sheet.export()

		# Set final frame
		self.frame_num += 200
		bpy.data.scenes[0].frame_end = self.frame_num
		
		# Make Pen movement Linear
		fcurves = self.pen.animation_data.action.fcurves
		for fcurve in fcurves:
			for kf in fcurve.keyframe_points:
				kf.interpolation = 'BEZIER'


		print(self.frame_num - self.starting_frame)
				
	
	
	
	def walk(self, step, vector_a, vector_b):
		if self.step:
			# Alter positions
			vector_a = vector_a.hadamard(self.scale)
			vector_a = vector_a.sum(self.delta)
			
			vector_b = vector_b.hadamard(self.scale)
			vector_b = vector_b.sum(self.delta)
			
			vector = vector_a.new()
			
			# Making sure there are no gaps
			vector_step_keyframe = vector_b.subtract(vector_a).divide(step)
			vector_step_sheet = vector_step_keyframe.divide(self.dots_per_keyframe)
			
			
			for _ in range(int(step)):
				# Executed for every frame
				bpy.context.scene.frame_set(self.frame_num)
				
				for _ in range(self.dots_per_keyframe):
					self.sheet.write(vector.to_point())
					vector = vector.sum(vector_step_sheet)
				
				self.sheet.add_frame()
				self.frame_num += 1

			
			
	
	
	
	def add_keyframe_write(self, vector):
		bpy.context.scene.frame_set(self.frame_num)
		# Alter pen position
		pen_vector = vector.hadamard(self.scale)
		pen_vector = pen_vector.sum(self.delta)
		self.pen.location = pen_vector.to_tuple()
		
		# Alter pen holder position
		pen_holder_vector = vector.hadamard(self.scale)
		pen_holder_vector = pen_holder_vector.sum(self.delta)
		pen_holder_vector = pen_holder_vector.sum(V(2 + math.sin(vector.x * 2 * math.pi), 0.5, 3))
		pen_holder_vector = pen_holder_vector.sum(pen_vector.subtract(pen_holder_vector).divide(2))
		self.pen_holder.location = pen_holder_vector.to_tuple()
		
		# Insert keyframes
		self.pen.keyframe_insert(data_path='location', index=-1)
		self.pen_holder.keyframe_insert(data_path='location', index=-1)
	


	def add_keyframes_write(self, vectors, vector_last):
		
		# Add keyframes
		v = vectors[0].hadamard(self.distance_scale)
		v_last = vector_last.hadamard(self.distance_scale)
		self.walk(math.ceil(self.step * v.eucledian(v_last)), vector_last, vectors[0])

		self.add_keyframe_write(vectors[0])
		
		for i in range(1, len(vectors)):
			v = vectors[i].hadamard(self.distance_scale)
			v_last = vectors[i-1].hadamard(self.distance_scale)
			self.walk(math.ceil(self.step * v.eucledian(v_last)), vectors[i-1], vectors[i])

			self.add_keyframe_write(vectors[i])
			


	def add_keyframe_pen(self, vector, frame, holder_offset=V(0, 0, 0), move_z=False):
		bpy.context.scene.frame_set(frame)

		self.pen.location = vector.to_tuple()
		
		pen_holder_vector = vector.sum(V(2, 0.5, 3)).sum(holder_offset)
		pen_holder_vector = pen_holder_vector.sum(vector.subtract(pen_holder_vector).divide(2))
		self.pen_holder.location.x = pen_holder_vector.to_tuple()[0]
		self.pen_holder.location.y = pen_holder_vector.to_tuple()[1]
		if move_z:
			self.pen_holder.location.z = pen_holder_vector.to_tuple()[2]
		
		self.pen.keyframe_insert(data_path='location', index=-1)
		self.pen_holder.keyframe_insert(data_path='location', index=-1)

		while self.frame_num < frame:
			self.sheet.add_frame()
			self.frame_num += 1


	def add_keyframe(self, obj, location, frame, rotation=None):
		bpy.context.scene.frame_set(frame)

		# Location
		obj.location = location
		obj.keyframe_insert(data_path='location', index=-1)

		# Rotation
		if rotation:
			obj.rotation_euler = rotation
			obj.keyframe_insert(data_path='rotation_euler', index=0, frame=frame)

		while self.frame_num < frame:
			self.sheet.add_frame()
			self.frame_num += 1


