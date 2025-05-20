''' 
Gathering data and training labels
Data is saved in foo.csv in working directory
'''
import pygame
import multiprocessing
import numpy as np
import time

import common as c
from paddle import Paddle
from square import Square

from pyomyo import Myo, emg_mode

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q, MODE):
	m = Myo(mode=MODE)
	m.connect()

	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	 # Orange logo and bar LEDs
	m.set_leds([128, 128, 0], [128, 128, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)

	"""worker function"""
	while True:
		m.run()
	print("Worker Stopped")

# -------- Main Program Loop -----------
if __name__ == "__main__":
	score = 0
	lives = 3
	MOVE_SPEED = 10

	# Experiment vars
	MODE = emg_mode.PREPROCESSED
	TIMER = True

	start_time = time.time()
	start_time_ns = time.perf_counter_ns() 
	last_toggle_time = time.time()
	p = multiprocessing.Process(target=worker, args=(q,MODE,))
	p.start()

	# PyGame setup 
	pygame.init()

	# Open a new window
	size = (c.WIN_X, c.WIN_Y)
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Breakout Game")
	 
	# This will be a list that will contain all the sprites we intend to use in our game.
	all_sprites_list = pygame.sprite.Group()
	 
	# Create the Paddle
	paddle = Paddle(c.LIGHTBLUE, c.PADDLE_X, c.PADDLE_Y)
	paddle.rect.x = (c.WIN_X - c.PADDLE_X)//2
	paddle.rect.y = int((c.WIN_Y * 7/8))

	#Create the Circle
	square = Square(c.LIGHTBLUE, c.PADDLE_X, c.PADDLE_X)
	square.rect.x = (c.WIN_X - c.PADDLE_X)//2
	square.rect.y = int((c.WIN_Y * 6/8))
	
	# Add the paddle to the list of sprites
	all_sprites_list.add(paddle)

	# The loop will carry on until the user exit the game (e.g. clicks the close button).
	carryOn = True
	 
	# The clock will be used to control how fast the screen updates
	clock = pygame.time.Clock()

	paddle_dir = MOVE_SPEED

	#data1 = ['One', 'Two', 'Three', "Four", "Five", "Six", "Seven", "Eight", "Rect", "Time"]
	data1 = []
	#data2 = ['One', 'Two', 'Three', "Four", "Five", "Six", "Seven", "Eight", "Square (0 or 1)", "Time"]
	data2 = []
	time_elapsed = time.time() - start_time
	squareAlive = False
	rectLeft = True
	rectMid = False
	rectRight = False
	while carryOn:
		if time_elapsed < 120:
			# --- Main event loop
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					carryOn = False # Flag that we are done so we exit this loop


			# paddle.rect.x += paddle_dir

			curr_time = time.time() - last_toggle_time
			if curr_time >= 3:
				last_toggle_time = time.time()
				#toggle
				
				if rectMid:
					paddle.rect.x = 1300
					rectMid = False
					rectRight = True
				elif rectRight: #rectRight
					paddle.rect.x = 100
					rectRight = False
					rectLeft = True
				else:
					paddle.rect.x = 700
					rectLeft = False
					rectMid = True
			
			# # If we hit a wall
			# if (paddle.rect.x >= c.WIN_X - c.PADDLE_X):
			# 	# Went too far right, go left
			# 	paddle_dir = -1 * MOVE_SPEED
			# elif (paddle.rect.x <= 0):
			# 	# Went too far left, go right
			# 	paddle_dir = MOVE_SPEED

			# Deal the the data from the Myo
			# The queue is now full of all data recorded during this time step
			while not(q.empty()):
				threshold1 = -.5
				threshold2 = .5
				d1 = list(q.get())
				min_maxed_paddle = 2 * paddle.rect.x / 1400 - 1
				print("min_maxed_paddle", min_maxed_paddle)
				# d1.append(min_maxed_paddle)
				if min_maxed_paddle < threshold1:
					d1.append(-1)
				elif min_maxed_paddle >= threshold1 and min_maxed_paddle < threshold2:
					d1.append(0)
				else:
					d1.append(1)
				d1.append(time.perf_counter_ns() - start_time_ns)
				data1.append(d1)
				
			# --- Game logic should go here
			all_sprites_list.update()

			# --- Drawing code should go here
			# First, clear the screen to dark blue.
			screen.fill(c.DARKBLUE)
			pygame.draw.line(screen, c.WHITE, [0, 38], [c.WIN_X, 38], 2)
		
			#Display the score and the number of lives at the top of the screen
			font = pygame.font.Font(None, 34)
			text = font.render("Score: " + str(score), 1, c.WHITE)
			screen.blit(text, (int(c.WIN_X * 1/8),10))
			text = font.render("Lives: " + str(lives), 1, c.WHITE)
			screen.blit(text, (int(c.WIN_X * 7/8),10))
		
			# Display message about training data
			font = pygame.font.Font(None, 82)
			text = font.render("Keeping your arm still", 10, c.WHITE)
			screen.blit(text, (int(c.WIN_X * 1/4) - 41, int(c.WIN_Y/2) - 60 ))
			text = font.render("Use your wrist to follow the paddle", 10, c.WHITE)
			screen.blit(text, (int(c.WIN_X * 1/4) - 41,int(c.WIN_Y/2)))

			#Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
			all_sprites_list.draw(screen)
		
			# --- Go ahead and update the screen with what we've drawn.
			pygame.display.flip()
		
			# --- Limit to 60 frames per second
			clock.tick(60)

			# Moving the paddle when the use uses the arrow keys
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT]:
				paddle.moveLeft(c.PADDLE_SPEED)
			if keys[pygame.K_RIGHT]:
				paddle.moveRight(c.PADDLE_SPEED)
			if keys[pygame.K_SPACE]:		
				carryOn = False
		elif time_elapsed < 240: #IN THE ITEM THROWING PORTION OF TRAINING
			while not(q.empty()):
				d2 = list(q.get())
				d2.append(1 if squareAlive else 0)
				d2.append(time.perf_counter_ns() - start_time_ns)
				data2.append(d2)

			screen.fill(c.WHITE)
			# Display message about training data
			font = pygame.font.Font(None, 82)
			text = font.render("Close your fist when square appears", 10, c.DARKBLUE)
			screen.blit(text, (int(c.WIN_X * 1/8) - 41, int(c.WIN_Y/2) - 60 ))
			text = font.render("Open your hand flat when square disappears", 10, c.DARKBLUE)
			screen.blit(text, (int(c.WIN_X * 1/8) - 41,int(c.WIN_Y/2)))

			all_sprites_list.remove(paddle)
			
			curr_time = time.time() - last_toggle_time
			if curr_time >= 3:
				last_toggle_time = time.time()
				#toggle
				if squareAlive:
					all_sprites_list.remove(square)
					squareAlive = False
				else:
					all_sprites_list.add(square)
					squareAlive = True

			all_sprites_list.draw(screen)
			pygame.display.flip()
		else:
			carryOn = False

		time_elapsed = time.time() - start_time
			
	if carryOn == False:	
		# First, handle paddle data saving
		np_data1 = np.asarray(data1)
		np.savetxt("foo.csv", np_data1, delimiter=",")
		print("Data Saved in foo.csv")	

		#Then, handle item data saving
		np_data2 = np.asarray(data2)
		np.savetxt("bar.csv", np_data2, delimiter=",")
		print("Data Saved in bar.csv")	

		pygame.quit()
		p.terminate()
		p.join()
	 
	# Once we have exited the main program loop we can stop the game engine:
	pygame.quit()