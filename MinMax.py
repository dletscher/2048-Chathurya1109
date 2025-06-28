from Game2048 import BasePlayer
import time
import math

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._lastDepth = 0
        self._moveCount = 0
        self._timeBuffer = 0.1  # Increased time buffer
        self._minDepth = 2  # Minimum search depth
        
    def findMove(self, state):
        self._moveCount += 1
        start_time = time.time()
        end_time = start_time + self._timeLimit - self._timeBuffer
        
        def time_remaining():
            return time.time() < end_time
        
        # Get valid actions with fallback
        actions = state.actions()
        if not actions:
            self.setMove('L')  # Should never happen as gameOver would be True
            return
            
        # Initialize with simple greedy choice as ultimate fallback
        best_move = self.get_greedy_move(state) or actions[0]
        best_score = -float('inf')
        depth = 1
        
        # Iterative deepening with multiple safety checks
        while time_remaining() and depth <= 8:  # Reasonable depth limit
            self._lastDepth = depth
            current_best = None
            current_score = -float('inf')
            
            # Search all actions with move ordering
            ordered_actions = self.orderMoves(state)
            for action in ordered_actions:
                if not time_remaining():
                    break
                    
                new_state = state.move(action)
                if new_state is None:
                    continue
                    
                score = self.alphabeta(
                    new_state, 
                    depth-1, 
                    -float('inf'), 
                    float('inf'), 
                    False
                )
                
                if score is None:  # Timeout during search
                    break
                    
                if score > current_score:
                    current_score = score
                    current_best = action
            
            # Update best move if search completed
            if time_remaining() and current_best is not None:
                best_move = current_best
                best_score = current_score
                depth += 1
            else:
                break  # Timeout occurred
        
        # Final validation - ensure we never return None
        if best_move not in actions:
            best_move = self.get_greedy_move(state) or actions[0]
        
        self.setMove(best_move)
    
    def get_greedy_move(self, state):
        """Fallback method that always returns a valid move"""
        actions = state.actions()
        if not actions:
            return None
            
        # Choose move that creates most empty spaces
        best_move = actions[0]
        max_empty = -1
        for action in actions:
            new_state = state.move(action)
            if new_state:
                empty = sum(1 for i in range(16) if new_state._board[i] == 0)
                if empty > max_empty:
                    max_empty = empty
                    best_move = action
        return best_move
    
    def alphabeta(self, state, depth, alpha, beta, isMax):
        if not self.timeRemaining():
            return None
            
        if state.gameOver():
            return -100000
            
        if depth == 0:
            return self.evaluate(state)
            
        if isMax:
            value = -float('inf')
            for action in self.orderMoves(state):
                new_state = state.move(action)
                if new_state is None:
                    continue
                    
                result = self.alphabeta(new_state, depth-1, alpha, beta, False)
                if result is None:
                    return None
                    
                value = max(value, result)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            possible_tiles = state.possibleTiles()
            if not possible_tiles:
                return self.evaluate(state)
                
            # Consider worst-case scenario
            for pos, val in possible_tiles:
                new_state = state.addTile(pos, val)
                result = self.alphabeta(new_state, depth-1, alpha, beta, True)
                if result is None:
                    return None
                    
                value = min(value, result)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    
    def orderMoves(self, state):
        """Order moves based on immediate board quality"""
        actions = state.actions()
        if not actions:
            return []
            
        scored_moves = []
        for action in actions:
            new_state = state.move(action)
            if new_state is None:
                continue
            score = self.simple_evaluate(new_state)
            scored_moves.append((score, action))
        
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [action for (score, action) in scored_moves]
    
    def simple_evaluate(self, state):
        """Fast evaluation for move ordering"""
        empty = sum(1 for i in range(16) if state._board[i] == 0)
        return empty * 10 + state.getScore() / 100
    
    def evaluate(self, state):
        """Comprehensive evaluation function"""
        if state.gameOver():
            return -100000
            
        score = state.getScore()
        empty = sum(1 for i in range(16) if state._board[i] == 0)
        max_tile = max(state._board)
        
        # Smoothness
        smoothness = 0
        for i in range(4):
            for j in range(3):
                smoothness -= abs(state.getTile(i, j) - state.getTile(i, j+1))
        for j in range(4):
            for i in range(3):
                smoothness -= abs(state.getTile(i, j) - state.getTile(i+1, j))
        
        # Monotonicity
        mono = 0
        for i in range(4):
            row = [state.getTile(i, j) for j in range(4)]
            mono += self.monotonicity(row)
        for j in range(4):
            col = [state.getTile(i, j) for i in range(4)]
            mono += self.monotonicity(col)
        
        # Corner strategy
        corner = state.getTile(0, 0)
        corner_bonus = math.log2(corner + 1) * 10 if corner == max_tile else 0
        
        return (
            score * 1.0 + 
            empty * 100.0 + 
            math.log2(max_tile + 1) * 200.0 + 
            smoothness * 2.0 + 
            mono * 1.5 + 
            corner_bonus
        )
    
    def monotonicity(self, sequence):
        """Calculate sequence monotonicity"""
        if len(sequence) < 2:
            return 0
            
        increasing = decreasing = 0
        for i in range(len(sequence)-1):
            if sequence[i] > sequence[i+1]:
                decreasing += sequence[i] - sequence[i+1]
            elif sequence[i] < sequence[i+1]:
                increasing += sequence[i+1] - sequence[i]
                
        return max(increasing, decreasing) - min(increasing, decreasing)
    
    def stats(self):
        print(f"Average search depth: {self._lastDepth}")
        print(f"Total moves made: {self._moveCount}")