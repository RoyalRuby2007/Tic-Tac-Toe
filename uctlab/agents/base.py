class Agent:
    """Nhận vào một thế cờ, trả về một nước đi.
    Sau mỗi lần gọi, self.info chứa thống kê của lượt tìm kiếm đó:
      {"time": giây, "nodes": int, "iterations": int,
       "root": [(move, N, W, Q), ...]}   # "root" chỉ MCTS mới có
    """
    name = "agent"
    def __init__(self): self.info = {}
    def select_move(self, state): raise NotImplementedError
    def reset(self): pass                # gọi ở đầu mỗi ván