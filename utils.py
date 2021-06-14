import csv





def leftmost(positions):
	min = positions[0]
	for position in positions:
		if position[0] < min[0]:
			min = position
	return min

def rightmost(positions):
	max = positions[0]
	for position in positions:
		if position[0] > max[0]:
			max = position
	return max

    
    
def load_font_csv(filename):
	font = {}
	from_to = {}

	with open(filename, 'r') as file:
		reader = csv.reader(file)

		for line in reader:
			if line:
				points = []
				for string in line[1:]:
					l = string.split(', ')
					if not l[0]: continue
					point = (float(l[0]), float(l[1]), float(l[2]))
					points.append(point)
				if not points: continue
				font[line[0]] = points
				from_to[line[0]] = (leftmost(points)[0], rightmost(points)[0])

	return font, from_to



def load_font_txt(filename):
	font = {}
	from_to = {}

	with open(filename, 'r') as file:
		lines = file.readlines()

		for line in lines:
			if line:
				line_split = line.split(',"')
				points = []
				for string in line_split[1:]:
					l = string.replace('"', '').split(', ')
					print(string[:-1])
					if not l[0]: continue
					point = (float(l[0]), float(l[1]), float(l[2]))
					points.append(point)

				if not points: continue
				font[line[0]] = points
				from_to[line[0]] = (leftmost(points)[0], rightmost(points)[0])

	return font, from_to