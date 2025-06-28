from Game2048 import Game2048
import sys, importlib, argparse, time

def play(agent, graphicsSize, delay):
    state = Game2048()
    state.randomize()

    if graphicsSize is not None:
        from Graphics import Graphics
        g = Graphics(graphicsSize)
        g.draw(state)
    else:
        g = None

    while not state.gameOver():
        print(state)

        agent._startTime = time.time()
        agent.findMove(state)
        move = agent.getMove()

        print(f"\n[INFO] Chosen move: {move}\n")

        if move is None:
            print("[ERROR] Agent returned None move. Exiting...")
            print(state)
            break

        state, reward = state.result(move)

        if g is not None:
            g.draw(state)

        if delay:
            time.sleep(delay)

    print(state)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play 2048 Game')
    parser.add_argument('agent', type=str, help="Agent module name")
    parser.add_argument('time_limit', type=float, help="Time limit per move")
    parser.add_argument('-g', type=int, help="Graphics window size")
    parser.add_argument('-t', type=float, help="Time delay between moves")
    parser.add_argument('-d', type=str, help="Data file to load")

    args = parser.parse_args()

    try:
        agentModule = importlib.import_module(args.agent.split('.')[0])
    except ImportError:
        print('[ERROR] Invalid agent module.')
        sys.exit()

    timeLimit = args.time_limit
    agent = agentModule.Player(timeLimit)

    if args.d:
        agent.loadData(args.d)

    play(agent, args.g, args.t)
