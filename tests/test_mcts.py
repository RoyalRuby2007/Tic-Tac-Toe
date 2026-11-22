"""Test cho MCTS bản Python (issue #4, #5).

Chạy:  uv run pytest -q tests/test_mcts.py
"""
from uctlab.agents.mcts import MCTSAgent
from uctlab.games.base import DRAW, ONGOING
from uctlab.games.mnk import MNKState


def board(*moves, m=3, n=3, k=3):
    """Tạo thế cờ bằng cách đi lần lượt các ô (hàng, cột), X đi trước.
    Hàng 0 là hàng trên cùng."""
    s = MNKState(m, n, k)
    for r, c in moves:
        s.play(r * n + c)
    return s


def example_from_assignment():
    """Thế cờ trong đề, X (người 1) đi:
        O | X | .
        . | O | .
        X | . | .
    """
    return board((0, 1), (0, 0), (2, 0), (1, 1))


def test_sum_of_root_visits_equals_iterations():
    agent = MCTSAgent(iterations=500, seed=0)
    agent.select_move(example_from_assignment())
    assert sum(ch.N for ch in agent.root.children) == 500
    assert agent.root.N == 500


def test_example_from_assignment_blocks_diagonal():
    s = example_from_assignment()
    move = MCTSAgent(iterations=2000, seed=1).select_move(s)
    assert move == 2 * 3 + 2            # ô (2,2) = dưới-phải
    assert s.move_str(move) == "c1"


def test_takes_immediate_win():
    # X: (0,0),(0,1)  O: (1,0),(1,1)  -> X đi (0,2) là thắng
    s = board((0, 0), (1, 0), (0, 1), (1, 1))
    assert MCTSAgent(iterations=1000, seed=2).select_move(s) == 2


def test_blocks_opponent_win():
    # X: (0,0),(2,2)  O: (1,0),(1,1)  -> O doạ (1,2), X phải chặn
    s = board((0, 0), (1, 0), (2, 2), (1, 1))
    assert MCTSAgent(iterations=2000, seed=3).select_move(s) == 1 * 3 + 2


def test_same_seed_same_move():
    s = MNKState(3, 3, 3)
    a = MCTSAgent(iterations=300, seed=42).select_move(s)
    b = MCTSAgent(iterations=300, seed=42).select_move(s)
    assert a == b


def test_does_not_modify_input_state():
    s = example_from_assignment()
    before = list(s.legal_moves())
    MCTSAgent(iterations=200, seed=0).select_move(s)
    assert list(s.legal_moves()) == before


def test_self_play_3x3_is_draw():
    for g in range(4):
        s = MNKState(3, 3, 3)
        agents = {1: MCTSAgent(iterations=3000, seed=10 + g),
                  2: MCTSAgent(iterations=3000, seed=20 + g)}
        while s.result() == ONGOING:
            s.play(agents[s.player].select_move(s))
        assert s.result() == DRAW
