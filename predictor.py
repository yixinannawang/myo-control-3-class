import common as c


class Predictor:
	def __init__(self):
		self.data = []
		self.last_pred = c.WIN_X
		self.pred = 0
		self.model = None

	def simple_predict(self, data, scale=3000):
		print("data:", data)
		arr = max(data)
		print("arr:", arr)
		# pred_paddle_pos = ((sum(arr[:])/scale) * c.WIN_X) - c.PADDLE_X
		pred_paddle_pos = ((sum(arr[:])/scale) * c.WIN_X)
		

		# Stop small gitters
		if ( abs(pred_paddle_pos-self.last_pred) /c.WIN_X > 0.05 ):
			# We have made a big change, so its worth updating the position
			self.pred = pred_paddle_pos

		self.last_pred = pred_paddle_pos
		return self.pred


	def predict(self, left_data, right_data):
		pred_paddle_pos = c.WIN_X * max(right_data)/800

		# Stop small gitters
		if ( abs(pred_paddle_pos-self.last_pred)/c.WIN_X > 0.1 ):
			# We have made a big change, so its worth updating the position
			self.pred = pred_paddle_pos

		self.last_pred = pred_paddle_pos
		return self.pred

	def lin_regression(self, model, data):
		return model.predict(data)
	
	def svm(self, model, data):
		return model.predict(data)