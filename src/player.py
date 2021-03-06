#!/usr/bin/env python
# -*- coding: utf-8 *-*

from random import randint
from numpy import sign

from const import *
from helper import *
import sprites

class Player(object):
	"""class for player; everything static"""

	@classmethod
	def init(cls, world, pos):
		cls.W = world
		if pos != None:
			cls.x, cls.y = pos
		else:
			m = cls.W.cur_dungeon()
			x, y = DUNGEON_X/2, DUNGEON_Y/2
			while m.level[x][y] not in list(range(1,3)):
				x, y = randint(0, m.size_x-1), randint(0, m.size_y-1)
			cls.x = x
			cls.y = y
			cls.speed = R(SCALE/4)

			# movement
			cls.pX, cls.pY = 0, 0
			cls.moving = False # specifies if a movement operation is in progress
			cls.movement_dir = None # while moving: sets direction in which movement is performed
			cls.pixel_off_to_go = 0 # while moving: offset to go in a direction

			cls.W.cam_x = min(cls.x, m.size_x - X / SCALE) - cls.W.cam
			cls.W.cam_y = min(cls.y, m.size_y - Y / SCALE) - cls.W.cam
			# print cls.W.cam_x, m.size_x, X / SCALE, cls.W.cam

		cls.commands = [] # list of commands to execute; EventHandler writes to this; not in use yet
		#cls.sprite = sprites.CharSetMultiSprite("graphics/Chara1.png", 24,32, 4,0, 72,128)
		cls.sprite = sprites.CharSetMultiSprite("graphics/TheRevolverTrans.png", 32,32, 0,0, 0,0)
		cls.orientation = 1


	@classmethod
	def handle_movement(cls):
		if cls.moving:
			cls.movement_in_progress()
			cls.commands = []
		else:
			dung = cls.W.cur_dungeon()
			#print "called handle_movement"
			for com in cls.commands:
				#print 'got key', k
				if com == Dir.N:
					if cls.y > 0 and dung.level[cls.x][cls.y-1] != 0:
						cls.prepare_movement(com) # cls.y -= 1
					if cls.y > cls.W.cam - 1 and cls.y - cls.W.cam < cls.W.cam_y:
						cls.W.cam_y -= 1
				if com == Dir.E:
					cls.orientation = 0
					if cls.x < dung.size_x - 1 and dung.level[cls.x+1][cls.y] != 0:
						cls.prepare_movement(com) # cls.x += 1
					if cls.x + cls.W.cam - 1 < dung.size_x and cls.x + cls.W.cam > cls.W.cam_x + X / SCALE:
						cls.W.cam_x += 1
				if com == Dir.S:
					if cls.y < dung.size_y - 1 and dung.level[cls.x][cls.y+1] != 0:
						cls.prepare_movement(com) # cls.y += 1
					if cls.y + cls.W.cam - 1 < dung.size_y and cls.y + cls.W.cam > cls.W.cam_y + Y / SCALE:
						cls.W.cam_y += 1
					#print cls.y, cls.W.cam, cls.W.cam_y, Y / SCALE, dung.size_y
				if com == Dir.W:
					cls.orientation = 1
					if cls.x > 0 and dung.level[cls.x-1][cls.y] != 0:
						cls.prepare_movement(com) # cls.x -= 1
					if cls.x > cls.W.cam - 1 and cls.x - cls.W.cam < cls.W.cam_x:
						cls.W.cam_x -= 1
			cls.commands = [] # ohne das gibts seltsame glitches ^^
			cls.pill_level()

	# LEGACY STUB; just for working sake
	@classmethod
	def prepare_movement(cls, direc):
		cls.moving = True
		cls.movement_dir = direc
		if direc == Dir.N:
			cls.y -= 1
		elif direc == Dir.E:
			cls.x += 1
		elif direc == Dir.S:
			cls.y += 1
		elif direc == Dir.W:
			cls.x -= 1

	#@classmethod
	#def prepare_movement(cls, direc):
	#	cls.moving = True
	#	cls.movement_dir = direc
	#	if direc == Dir.N:
	#		cls.pixel_off_to_go = -SCALE
	#	elif direc == Dir.E:
	#		cls.pixel_off_to_go = SCALE
	#	elif direc == Dir.S:
	#		cls.pixel_off_to_go = SCALE
	#	elif direc == Dir.W:
	#		cls.pixel_off_to_go = -SCALE

	@classmethod
	def movement_in_progress(cls):
		if cls.movement_dir == Dir.E or cls.movement_dir == Dir.W:
			cls.pX -= sign(cls.pixel_off_to_go) * cls.speed
		elif cls.movement_dir == Dir.N or cls.movement_dir == Dir.S:
			cls.pY -= sign(cls.pixel_off_to_go) * cls.speed
		if cls.pixel_off_to_go < 1:
			cls.pX = 0
			cls.pY = 0
			cls.moving = False
			#cls.movement_dir = None
			#cls.pixel_off_to_go = 0

	@classmethod
	def pill_level(cls):
		dung = cls.W.cur_dungeon()
		
		if not dung.pills:
			return

		for p in dung.pills:
			if p.x != cls.x or p.y != cls.y:
				continue

			if p.hp != 0:
				cls.W.H.lvl += (4-p.hp) * randint(2, 4) # +6,9,12 -12,18,24
				# cls.W.H.lvl += randint(4, 5)
				dung.pills

			dung.pills.remove(p)
			break

		p.hp = ([p.hp for p in dung.pills if cls.x == p.x and cls.y == p.y]+[0])[0]
		
