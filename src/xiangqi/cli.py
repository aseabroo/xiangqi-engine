from __future__ import annotations

from .game import Game, GameState
from .models import Position


def main() -> None:
    game = Game.new()
    print("Xiangqi Engine")
    print("Enter moves like 'a9 a8'. Type 'quit' to stop.")

    while game.state is GameState.ACTIVE:
        print()
        print(game.board)
        print(game.status())
        raw = input("> ").strip()
        if raw.lower() in {"quit", "exit", "q"}:
            return

        try:
            start_text, end_text = raw.split()
            start = Position.parse(start_text)
            end = Position.parse(end_text)
        except ValueError:
            print("Invalid input. Use two coordinates such as 'a9 a8'.")
            continue

        if not game.make_move(start, end):
            print("Illegal move.")

    print()
    print(game.board)
    print(game.status())


if __name__ == "__main__":
    main()
