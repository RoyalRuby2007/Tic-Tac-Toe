"""MCTS-UCT, bản Python dễ đọc (issue #4).

Một vòng lặp (iteration) gồm 4 bước:
    1. Selection        từ gốc đi xuống, mỗi tầng chọn con có UCT lớn nhất
    2. Expansion        tới nút còn nước chưa thử thì thêm 1 con mới
    3. Simulation       từ con mới, hai bên đánh ngẫu nhiên tới hết ván
    4. Backpropagation  cộng kết quả vào N, W của mọi nút trên đường đi

Quy ước quan trọng nhất: W của một nút tính theo góc nhìn của `mover`,
tức người VỪA ĐI nước dẫn tới nút đó. Nhờ vậy ở mọi tầng, nút cha chỉ cần
chọn con có điểm cao nhất (không phải đổi dấu).
Phần thưởng: thắng = 1, hoà = 0.5, thua = 0.
"""
import math
import random
import time

from ..games.base import ONGOING, DRAW
from .base import Agent


class Node:
    __slots__ = ("move", "parent", "mover", "children", "untried", "N", "W")

    def __init__(self, move, parent, mover, untried):
        self.move = move          # nước đi dẫn tới nút này (gốc: None)
        self.parent = parent      # nút cha (gốc: None)
        self.mover = mover        # người đã đi `move` (1 hoặc 2)
        self.children = []        # các con đã mở rộng
        self.untried = untried    # các nước hợp lệ CHƯA mở rộng thành con
        self.N = 0                # số lần thăm
        self.W = 0.0              # tổng phần thưởng, theo góc nhìn `mover`

    def uct(self, c):
        """W/N + c * sqrt(ln N_parent / N).  Chỉ gọi khi self.N > 0."""
        # TODO(1): viết đúng công thức trong đề, 1 dòng.
        return self.W / self.N + c * math.sqrt(math.log(self.parent.N) / self.N)


def reward(winner, mover):
    """Phần thưởng của `mover` khi ván kết thúc với `winner`
    (winner = DRAW, 1 hoặc 2)."""
    # TODO(2): hoà -> 0.5, mover thắng -> 1.0, còn lại -> 0.0
    if winner == DRAW:
        return 0.5
    return 1.0 if winner == mover else 0.0


class MCTSAgent(Agent):
    def __init__(self, iterations=1000, c=1.4, seed=None):
        super().__init__()
        self.iterations = iterations
        self.c = c
        self.rng = random.Random(seed)   # MỌI lựa chọn ngẫu nhiên đều dùng self.rng
        self.name = f"MCTS(it={iterations},c={c})"
        self.root = None                 # giữ lại cây sau mỗi lần tìm (để test, E4)

    def select_move(self, state):
        t0 = time.perf_counter()

        # Gốc: chưa có nước nào dẫn tới, mover = người KHÔNG phải đi lúc này.
        # TODO(3): tạo root = Node(...)
        root = Node(None , None , 3 - state.player , list(state.legal_moves()))

        for _ in range(self.iterations):
            s = state.clone()     # mỗi vòng làm trên bản sao, không đụng `state`
            node = root

            # --- 1. Selection ------------------------------------------------
            # TODO(4): khi nút đã mở rộng hết (không còn untried) VÀ có con:
            #          chọn con có uct(self.c) lớn nhất, rồi s.play(con.move)
            while not node.untried and node.children:
                node = max(node.children, key=lambda ch: ch.uct(self.c))
                s.play(node.move)
            # --- 2. Expansion ------------------------------------------------
            # TODO(5): nếu node còn untried:
            #          - lấy ngẫu nhiên 1 nước ra khỏi untried (dùng self.rng)
            #          - ghi lại mover = s.player TRƯỚC khi đi
            #          - s.play(nước đó)
            #          - tạo con với untried = list(s.legal_moves()), gắn vào node
            #          - node = con
            if node.untried:
                i = self.rng.randrange(len(node.untried))
                move = node.untried.pop(i)
                mover = s.player
                s.play(move)
                child = Node(move, node, mover, list(s.legal_moves()))
                node.children.append(child)
                node = child

            # --- 3. Simulation -----------------------------------------------
            # TODO(6): trong khi s.result() == ONGOING: đi 1 nước ngẫu nhiên
            while s.result() == ONGOING:
                s.play(self.rng.choice(s.legal_moves()))
            winner = s.result()   # DRAW, 1 hoặc 2

            # --- 4. Backpropagation ------------------------------------------
            # TODO(7): đi ngược từ node lên gốc (tới khi node is None):
            #          N += 1,  W += reward(winner, node.mover)
            while node is not None:
                node.N += 1
                node.W += reward(winner, node.mover)
                node = node.parent

        self.root = root
        # Chọn nước cuối cùng theo N LỚN NHẤT (không phải W/N) - xem E5.
        # TODO(8): best = con của root có N lớn nhất
        best = max(root.children, key=lambda ch: ch.N)
        self.info = {"iterations": self.iterations,
                     "time": time.perf_counter() - t0,
                     "root": self.root_stats(state)}
        return best.move

    def root_stats(self, state):
        """Bảng W, N, W/N của các con của gốc, sắp theo N giảm dần (dùng cho E4)."""
        rows = [{"move": state.move_str(ch.move), "N": ch.N, "W": ch.W,
                 "Q": ch.W / ch.N if ch.N else 0.0} for ch in self.root.children]
        return sorted(rows, key=lambda r: -r["N"])
