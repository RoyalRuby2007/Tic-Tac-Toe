"""Giao diện chung cho mọi trò chơi 2 người, tổng bằng không, thông tin đầy đủ."""
from abc import ABC, abstractmethod

ONGOING, DRAW = -1, 0          # result(): -1 chưa xong, 0 hoà, 1/2 là người thắng


class GameState(ABC):
    player: int                # người đến lượt: 1 (đi trước) hoặc 2

    @abstractmethod
    def legal_moves(self): """Danh sách nước hợp lệ; trả [] nếu ván đã kết thúc."""
    @abstractmethod
    def play(self, move): """Đi nước move, sửa trực tiếp trạng thái (in-place)."""
    @abstractmethod
    def undo(self): """Hoàn tác nước vừa đi."""
    @abstractmethod
    def clone(self): """Bản sao độc lập."""
    @abstractmethod
    def result(self): """ONGOING, DRAW, 1 hoặc 2."""

    def evaluate(self):            # điểm heuristic cho người đến lượt (Alpha-Beta cắt độ sâu)
        raise NotImplementedError
    def rollout(self, policy="random"):   # chơi tới hết ván, trả người thắng; KHÔNG sửa self
        raise NotImplementedError
    def move_str(self, move):
        return str(move)