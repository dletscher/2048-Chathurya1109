from Game2048 import BasePlayer

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._nodeCount = 0
        self._depthCount = 0

    def findMove(self, state):
        actions = state.actions()
        bestMove = actions[0] if actions else None
        depth = 1

        while self.timeRemaining():
            self._depthCount += 1
            bestVal = float('-inf')
            for action in actions:
                result = state.move(action)
                if not self.timeRemaining():
                    break
                value = self.minValue(result, depth - 1)
                if value is not None and value > bestVal:
                    bestVal = value
                    bestMove = action
            self.setMove(bestMove)
            depth += 1

    def maxValue(self, state, depth):
        if state.gameOver() or depth == 0:
            return self.evaluate(state)
        v = float('-inf')
        for action in state.actions():
            result = state.move(action)
            if not self.timeRemaining():
                return None
            val = self.minValue(result, depth - 1)
            if val is None:
                return None
            v = max(v, val)
        return v

    def minValue(self, state, depth):
        if state.gameOver() or depth == 0:
            return self.evaluate(state)
        v = float('inf')
        for action in state.actions():
            for result, prob in state.possibleResults(action):
                if not self.timeRemaining():
                    return None
                val = self.maxValue(result, depth - 1)
                if val is None:
                    return None
                v = min(v, val)
        return v

    def evaluate(self, state):
        empty = sum(1 for i in range(4) for j in range(4) if state.getTile(i, j) == 0)
        maxTile = max(state.getTile(i, j) for i in range(4) for j in range(4))
        return empty + (2 ** maxTile) * 0.1