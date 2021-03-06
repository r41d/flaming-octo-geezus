#!/usr/bin/env python
# -*- coding: utf-8 *-*

from random import randint, sample, choice

from const import *
from pill import Pill
from helper import R

ITER = 12

class GenerateMap(object):
	"""class which is responsible for the world generation"""
	def __init__(self, x, y):
		super(GenerateMap, self).__init__()

		# vars
		self.x, self.y = (x, y)
		self.map = [[0]*self.y for i in range(self.x)]
		self.rooms = []
		self.persistent_rooms = []
		self.persistent_corridors = []
		self.pills = []
		self.monster = []

		# generation calls
		self.split(0, self.x, 0, self.y, ITER)
		self.connect(self.rooms[randint(0, len(self.rooms)-1)])
		# self.spawn_objects()

	def split(self, xlo, xhi, ylo, yhi, iteration):
		# too small
		if min(xhi-xlo, yhi-ylo) < 4:
			# print 'broke after', ITER - iteration, 'iterations'
			return
			
		# generate room in splitted space
		if (xhi-xlo) * (yhi-ylo) <= 40 or iteration == 0:
			xlo += min(randint(0, R((xhi-xlo)*0.1)), 3)
			xhi -= min(randint(0, R((xhi-xlo)*0.1)), 3)

			ylo += min(randint(0, R((yhi-ylo)*0.1)), 3)
			yhi -= min(randint(0, R((yhi-ylo)*0.1)), 3)

			# set room
			self.set_room(xlo, xhi-1, ylo, yhi-1)

			# return for futher calculations
			return (xlo, xhi, ylo, yhi)
			
		if randint(0, 1):
			# Vertical Split "-"
			# x split value
			# it is between xlo and xhi but not too close (10%) of each ending
			var = R(xlo + (xhi-xlo)*0.45 + randint(0, R((xhi-xlo)*0.1)) )
			
			# recursive room generation
			self.split(xlo, var, ylo, yhi, iteration-1)
			self.split(var, xhi, ylo, yhi, iteration-1)

		else:
			# Horizontal Split "|"
			var = R(ylo + (yhi-ylo)*0.45 + randint(0, R((yhi-ylo)*0.1)))
			
			# recursive room generation
			self.split(xlo, xhi, ylo, var, iteration-1)
			self.split(xlo, xhi, var, yhi, iteration-1)

	def set_room(self, xlo, xhi, ylo, yhi):
		# print "room", xlo, xhi, ylo, yhi

		room = []
		for x in range(xlo, xhi):
			for y in range(ylo, yhi):
				self.map[x][y] = 1
				room.append((x,y))

		self.rooms.append(room)
		self.spawn_objects(room, 1)

		# export rooms for drawing
		self.persistent_rooms.append( ( (xlo,ylo), (xhi,ylo), (xlo,yhi), (xhi,yhi) ) )

	def rand_room(self, lo, hi):
		return randint(lo, hi), randint(lo, hi)

	def set_connect(self, xlo, xhi, ylo, yhi):
		# print "connect", xlo, xhi, ylo, yhi
		corridor = []

		for x in range(xlo, xhi+1):
			for y in range(ylo, yhi+1):
				if self.map[x][y] == 0:
					corridor.append((x,y))
					self.map[x][y] = 2

		# export corridors
		self.persistent_corridors.append( ( (xlo,ylo), (xhi,yhi) ) )

		# spawn hard pills based on luck and length
		if randint(0, 3) * randint(0, self.manhatten((xlo, ylo), (xhi, yhi))-1) > 0:
			self.spawn_objects(corridor, 10)

	def connect(self, a):
		# everything is connected
		if len(self.rooms) <= 1:
			return

		b = self.closest_room(a)
		self.rooms.remove(a)
		# print "to remove", b
		if b: self.rooms.remove(b) # if b because this crashed for no reason
		self.rooms.append(a+b)
		pa, pb = self.room_dist_pair(a, b)

		# print pa, pb

		if pa[0] == pb[0]:
			self.set_connect(pa[0], pa[0], min(pa[1], pb[1]), max(pa[1], pb[1]))
		elif pa[1] == pb[1]:
			self.set_connect(min(pa[0], pb[0]), max(pa[0], pb[0]), pa[1], pa[1])
		else:
			if randint(0,1):
				# pc = (pa[0], pb[1])
				self.set_connect(pa[0], pa[0], min(pa[1], pb[1]), max(pa[1], pb[1]))
				self.set_connect(min(pa[0], pb[0]), max(pa[0], pb[0]), pb[1], pb[1])
			else:
				# pc = (pb[0], pa[1])
				self.set_connect(pb[0], pb[0], min(pa[1], pb[1]), max(pa[1], pb[1]))
				self.set_connect(min(pa[0], pb[0]), max(pa[0], pb[0]), pa[1], pa[1])

		# new recursion
		self.connect(a+b)

	def closest_room(self, room):
		val, ref = self.room_dist(room, self.rooms[0]), self.rooms[0]
		for b in self.rooms:
			# skip trivial solution
			if b == room:
				continue

			# check for minimum
			if self.room_dist(room, b) < val:
				val = self.room_dist(room, b)
				ref = b

		return ref

	def room_dist(self, a, b):
		# pa is pixel of room a
		return min(self.manhatten(pa, pb) for pa in a for pb in b)

	def room_dist_pair(self, a, b):
		val = float('infinity')
		for pa in a:
			for pb in b:
				if self.manhatten(pa, pb) < val:
					val = self.manhatten(pa, pb)
					refa = [pa]
					refb = [pb]
				elif self.manhatten(pa, pb) == val:
					refa.append(pa)
					refb.append(pb)
		
		k = randint(0, len(refa)-1)

		return refa[k], refb[k]

	def manhatten(self, pa, pb):
		return abs(pa[0]-pb[0]) + abs(pa[1]-pb[1])

	def spawn_objects(self, room, hp):
		# error prevention
		if not room:
			return

		x, y = sample(room, 1)[0]
		self.pills.append(Pill(x, y, hp))


class GenerateMap2(object):
	def __init__(self, x, y):
		self.x, self.y = (300, 300)
		self.map = [[0]*self.y for i in range(self.x)]
		for _ in range(10):
			x1, x2 = sorted(sample(range(0,self.x), 2))
			y1, y2 = sorted(sample(range(0,self.y), 2))
			for xx in range(x1,x2):
				for yy in range(y1,y2):
					self.map[xx][yy] = 1


class GenerateMapTetris(object):
	"""class which is responsible for the world generation"""
	def __init__(self, x, y):
		super(GenerateMap, self).__init__()
		self.x, self.y = (x, y)
		self.map = [[0]*self.y for i in range(self.x)]
		# self.gen_rooms(0, self.x, 0, self.y, 4)
		self.gen_rooms(4, 7, 5)

	def gen_rooms(self, lo, hi, count):
		room = self.rand_room(lo, hi)
		xoff, yoff = R((self.x-room[0])/2), R((self.y-room[1])/2)
		self.set_room(xoff, xoff + room[0], yoff, yoff + room[1])

		for _ in range(count): # room
			room = self.rand_room(lo, hi)

			for _1 in sample(range(4), 4):
				# rotate array
				self.map = [list(t) for t in zip(*self.map[::-1])]
				# print self.map

				limit = len(self.map)

				depth = [0] * limit
				# check maximum depth
				for z in range(limit):
					for d in range(len(self.map[0])):
						if self.map[z][d]:
							break
						depth[z] = d

				# calc deepest size
				val, ind = min(depth[:room[0]]), 0
				for k in range(limit-room[0]+1):
					if min(depth[k:k+room[0]]) > val:
						ind = k

				if depth > room[0]:
					self.set_room(ind, ind + room[0], val - room[1], val)
					break

	def rand_room(self, lo, hi):
		return randint(lo, hi), randint(lo, hi)

	def set_room(self, xlo, xhi, ylo, yhi):
		# print xlo, xhi, ylo, yhi
		for x in range(xhi-xlo):
			for y in range(yhi-ylo):
				self.map[xlo+x][ylo+y] = 1

	def rotate(self, x, y, c):
		"MAGIC MAGIC MAGIC MAGIC MAGIC MAGIC <3"
		if c == 0:
			return x,y
		elif c == 1:
			return self.x - y, x
		elif c == 2:
			return self.x - x, self.y - y
		elif c == 3:
			return y, self.y - x


if __name__ == '__main__':
	import pprint;
	gen = GenerateMap()
	pprint.pprint(gen.map)
