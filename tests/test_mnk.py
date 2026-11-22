from uctlab.games.mnk import MNKState


def test_move_str_3x3():
    s = MNKState(3, 3, 3)
    assert s.move_str(0) == "a3"     # trên-trái
    assert s.move_str(2) == "c3"     # trên-phải
    assert s.move_str(6) == "a1"     # dưới-trái
    assert s.move_str(8) == "c1"     # dưới-phải


def test_parse_move_is_inverse_of_move_str():
    for m, n in [(3, 3), (9, 9), (15, 15)]:
        s = MNKState(m, n, 5 if m > 3 else 3)
        for move in range(m * n):
            assert s.parse_move(s.move_str(move)) == move