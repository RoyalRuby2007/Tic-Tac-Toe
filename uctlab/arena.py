def play_game(a1, a2, state):
    agents = {1: a1, 2: a2}
    while state.result() == -1:
        state.play(agents[state.player].select_move(state))
    return state.result()