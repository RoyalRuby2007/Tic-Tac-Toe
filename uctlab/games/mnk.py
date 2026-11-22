import numpy as np, random
from .base import GameState, ONGOING, DRAW

class MNKState(GameState):
    def __init__(self, m=3, n=3, k=3):
        self.m, self.n, self.k = m, n, k
        self.board = np.zeros(m * n, dtype=np.int8)
        self.player, self.history, self._result = 1, [], ONGOING

    def legal_moves(self):
        return [] if self._result != ONGOING else np.flatnonzero(self.board == 0).tolist()

    def _wins(self, idx, p):        # chỉ đếm 4 đường đi qua quân vừa đặt: O(k)
        r, c = divmod(idx, self.n)
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            cnt = 1
            for s in (1, -1):
                rr, cc = r + s * dr, c + s * dc
                while 0 <= rr < self.m and 0 <= cc < self.n and self.board[rr * self.n + cc] == p:
                    cnt += 1; rr += s * dr; cc += s * dc
            if cnt >= self.k: return True
        return False

    def play(self, mv):
        p = self.player; self.board[mv] = p; self.history.append(mv)
        if self._wins(mv, p): self._result = p
        elif len(self.history) == self.m * self.n: self._result = DRAW
        self.player = 3 - p

    def undo(self):
        self.board[self.history.pop()] = 0
        self._result, self.player = ONGOING, 3 - self.player

    def clone(self):
        s = MNKState(self.m, self.n, self.k)
        s.board, s.player = self.board.copy(), self.player
        s.history, s._result = list(self.history), self._result
        return s

    def result(self): return self._result

    def rollout(self, policy="random"):
        s = self.clone()
        while s.result() == ONGOING:
            s.play(random.choice(s.legal_moves()))
        return s.result()
    
    def move_str(self, move):
        """Số ô -> tên ô kiểu cờ vua. Ví dụ bàn 3x3: 8 -> 'c1', 0 -> 'a3'."""
        r, c = divmod(move, self.n)          # hàng (0 = trên cùng), cột
        return f"{chr(ord('a') + c)}{self.m - r}"

    def parse_move(self, s):
        """Tên ô -> số ô (ngược lại của move_str). Ví dụ 'c1' -> 8."""
        c = ord(s[0].lower()) - ord("a")
        r = self.m - int(s[1:])
        return r * self.n + c