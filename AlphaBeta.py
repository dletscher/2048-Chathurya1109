from Game2048 import *
import time

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._startTime = 0
        self._maxDepth = 4  # Tune based on performance

    def findMove(self, state):
        self._startTime = time.time()
        legalMoves = state.actions()
        bestMove = None
        bestScore = float('-inf')

        for move in legalMoves:
            result = state.move(move)
            if result is None:
                continue
            score = self.minValue(result, self._maxDepth - 1, float('-inf'), float('inf'))
            if score is not None and score > bestScore:
                bestScore = score
                bestMove = move

        if bestMove is None and legalMoves:
            bestMove = legalMoves[0]

        self.setMove(bestMove)

    def maxValue(self, state, depth, alpha, beta):
        if state.gameOver() or depth == 0 or not self.timeRemaining():
            return state.getScore()

        value = float('-inf')
        for move in state.actions():
            result = state.move(move)
            if result is None:
                continue
            val = self.minValue(result, depth - 1, alpha, beta)
            if val is None:
                return None
            value = max(value, val)
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cut-off
        return value

    def minValue(self, state, depth, alpha, beta):
        if state.gameOver() or depth == 0 or not self.timeRemaining():
            return state.getScore()

        value = float('inf')
        for index, tile in state.possibleTiles():
            result = state.addTile(index, tile)
            val = self.maxValue(result, depth - 1, alpha, beta)
            if val is None:
                return None
            value = min(value, val)
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cut-off
        return value