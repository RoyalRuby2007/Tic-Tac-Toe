from collections import Counter
from uctlab.games.mnk import MNKState
from uctlab.agents.random_agent import RandomAgent
from uctlab.arena import play_game

def test_random_vs_random_matches_known_rates():
    n = 20000
    c = Counter(play_game(RandomAgent(2*i), RandomAgent(2*i+1), MNKState()) for i in range(n))
    # Random vs Random trên 3×3: X thắng ≈ 58.5%, O ≈ 28.8%, hoà ≈ 12.7%
    assert abs(c[1]/n - 0.585) < 0.015 and abs(c[2]/n - 0.288) < 0.015 and abs(c[0]/n - 0.127) < 0.015

def test_undo_restores_board():
    s = MNKState(9, 9, 5); ref = s.board.copy()
    for mv in [40, 41, 30, 31, 50]: s.play(mv)
    for _ in range(5): s.undo()
    assert (s.board == ref).all() and s.player == 1