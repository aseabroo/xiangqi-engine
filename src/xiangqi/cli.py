from __future__ import annotations

from .game import Game, GameState
from .models import Position


def main() -> None:
    game = Game.new()
    print("Xiangqi Engine")
    print("Enter moves like 'a9 a8'. Commands: history, save FILE, load FILE, quit.")

    while game.state is GameState.ACTIVE:
        print()
        print(game.board)
        print(game.status())
        raw = input("> ").strip()
        lowered = raw.lower()

        if lowered in {"quit", "exit", "q"}:
            return

        if lowered == "history":
            if not game.history:
                print("No moves yet.")
            for index, move in enumerate(game.history, start=1):
                capture = f" x {move.captured.value}" if move.captured else ""
                check = " +" if move.gave_check else ""
                print(f"{index}. {move.mover.value} {move.piece.value} {move.start}-{move.end}{capture}{check}")
            continue

        if lowered.startswith("save "):
            path = raw[5:].strip()
            try:
                game.save(path)
                print(f"Saved to {path}")
            except OSError as error:
                print(f"Could not save game: {error}")
            continue

        if lowered.startswith("load "):
            path = raw[5:].strip()
            try:
                game = Game.load(path)
                print(f"Loaded {path}")
            except (OSError, ValueError) as error:
                print(f"Could not load game: {error}")
            continue

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
