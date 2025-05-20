
import multiprocessing
import argparse
import connection_manager
import numpy as np
import pandas as pd

import common as c
from pyomyo import Myo, emg_mode
from predictor import Predictor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC;

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.PREPROCESSED)
	m.connect()

	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	def print_battery(bat):
		print("Battery level:", bat)

	m.add_battery_handler(print_battery)

	# Orange logo and bar LEDs
	m.set_leds([128, 0, 0], [128, 0, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)

	"""worker function"""
	while True:
		m.run()
	print("Worker Stopped")

# -------- Main Program Loop -----------
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--ip', type=str, default='127.0.0.1')
	parser.add_argument('--port', type=int, default=-1)
	#parser.add_argument('--scale', type=int, default=3000)
	args = parser.parse_args()
	ip = args.ip
	port = args.port if args.port != -1 else None
	#scale = args.scale
	minP = 99999999.0
	maxP = -9999999.0


	# print("start LR training")
	# df = pd.read_csv('foo.csv')
	# emg_data = df.iloc[:, :-2]
	# paddle_data = df.iloc[:, -2]
	# lin_reg = LinearRegression()
	# lin_reg.fit(emg_data, paddle_data)
	# print("done fitting")
	df = pd.read_csv('foo.csv')
	emg_data = df.iloc[:, :-2]
	paddle_data = df.iloc[:, -2]
	svm_paddle = SVC()
	svm_paddle.fit(emg_data, paddle_data)

	print("start SVM training")
	df = pd.read_csv('bar.csv')
	emg_data = df.iloc[:, :-2]
	fist_data = df.iloc[:, -2]
	svm_fist = SVC()
	svm_fist.fit(emg_data, fist_data)
	print("done fitting")


	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()
	conn_manager = connection_manager.ConnectionManager(ip=ip, port=port, mode='client', shape=(-1,))

	# The loop will carry on until the user exit the game (e.g. clicks the close button).
	carryOn = True

	# Make a predictor
	pred_paddle_pos = 800 #middle
	predictor = Predictor()


	while carryOn:
		# --- Main event loop
		

		# Paddle prediction
		left_data = []
		right_data = []
		data = []

		while not(q.empty()):
			# Get the new data from the Myo queue
			d = list(q.get())
			left_data.append(d[7])
			right_data.append(d[2])
			data.append(d)

		if (len(right_data) > 0):
			# If we got new data, make a prediction
			# Custom predictor
			#pred_paddle_pos = predictor.predict(left_data, right_data)
			#pred_paddle_pos = predictor.simple_predict(data, scale=scale)
			
			pred_paddle_pos = predictor.svm(svm_paddle, data)
			print("predicted paddle position:", pred_paddle_pos)
			pred_throw = predictor.svm(svm_fist, data)
			print("predicted item throwing:", pred_throw)

			#scale to get range from -1 to 1
			#scaled_pos = pred_paddle_pos / ((maxP - minP)/2) - 1
			all_data = [pred_paddle_pos[-1], pred_throw[-1]]
			all_data = np.array(all_data).tobytes()
			conn_manager.sendall(all_data)
			print("sent data")


		# --- Game logic should go here
		'''
		#Check to see if paddle will go out of bounds
		if pred_paddle_pos > c.WIN_X:
			#Restrict paddle movement
			paddle.rect.x = c.WIN_X - c.PADDLE_X
		else:
			paddle.rect.x = pred_paddle_pos
		'''