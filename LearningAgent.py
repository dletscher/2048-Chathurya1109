import pickle
import random

from Game2048 import *

class Player(BasePlayer):
	def __init__(self, timeLimit):
		BasePlayer.__init__(self, timeLimit)
		
		# Initialize table
		self._valueTable = {}
		for a in range(16):
			for b in range(16):
				for c in range(16):
					for d in range(16):
						self._valueTable[(a,b,c,d)] = random.uniform(0,1)
						
		self._learningRate = .001
		self._discountFactor = .99
		
	def loadData(self, filename):
		print('Loading data')
		with open(filename, 'rb') as dataFile:
			self._valueTable = pickle.load(dataFile)
		
	def saveData(self, filename):
		print('Saving data')
		with open(filename, 'wb') as dataFile:
			pickle.dump(self._valueTable, dataFile)

	def value(self, board):
		# The table stores the value of the first row.
		# Look at all rotations and add there values so we 
		# also get the last row, first column and last column.
		v = 0.
		for turns in range(4):
			g = board.rotate(turns)
			v += self._valueTable[ tuple( g._board[:4] ) ]
			
		return v

	def findMove(self, board):
		bestValue = float('-inf')
		bestMove = ''
		
		for a in board.actions():
			# Finding the expected (or average) value of the state after the move is taken
			v = 0
			for (g, p) in board.possibleResults(a):
				v += p * self.value(g)
				
			if v > bestValue:
				bestValue = v
				bestMove = a
				
		self.setMove(bestMove)

	def train(self, repetitions):
		for trial in range(repetitions):
			print(f'Simulating game number {trial} of {repetitions}')
			
			state = Game2048()
			state.randomize()

			while not state.gameOver():
				self._startTime = time.time()
				self.findMove(state) # Currently does an on-policy search.  Should we do epsilon-greedy?
				move = self.getMove()
				oldState = state
				state, reward = state.result(move)
					
				# Update the table
				update = self._learningRate * (reward + self._discountFactor*self.value(state) - self.value(oldState))
				for turns in range(4):
					rotated = oldState.rotate(turns)
					self._valueTable[tuple(rotated._board[:4])] += update
					
					
		
if __name__ == '__main__':
	# Perform training
	a = Player(1)
	a.loadData('MyData')
	a.train(10000)
	a.saveData('MyData')
