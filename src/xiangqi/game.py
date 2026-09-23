from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .board import Board
from .models import Color, MoveRecord, PieceType, Position


class GameState(str, Enum):
    ACTIVE = "active"
    RED_WON = "red_won"
    BLACK_WON = "black_won"


@dataclass
class Game:
    board: Board
    turn: Color = Color.RED
    state: GameState = GameState.ACTIVE
    history: list[MoveRecord] = field(default_factory=list)

    @classmethod
    def new(cls) -> "Game":
        board = Board.initial()
        board.validate()
        return cls(board)

    def is_in_check(self, color: Color, board: Board | None = None) -> bool:
        board = board or self.board
        general = board.general_position(color)
        if general is None:
            return True

        for start, piece in board.pieces.items():
            if piece.color is color.opponent and board.piece_rule_allows(start, general):
                return True
        return False

    def is_legal_move(self, start: Position, end: Position, color: Color | None = None) -> bool:
        color = color or self.turn
        piece = self.board.piece_at(start)
        if piece is None or piece.color is not color:
            return False

        target = self.board.piece_at(end)
        if target is not None and target.kind is PieceType.GENERAL:
            return False

        if not self.board.piece_rule_allows(start, end):
            return False

        candidate = self.board.copy()
        candidate.move(start, end)
        return not self.is_in_check(color, candidate)

    def legal_moves(self, color: Color | None = None) -> list[tuple[Position, Position]]:
        color = color or self.turn
        moves: list[tuple[Position, Position]] = []
        starts = [position for position, piece in self.board.pieces.items() if piece.color is color]
        for start in starts:
            for row in range(10):
                for col in range(9):
                    end = Position(row, col)
                    if self.is_legal_move(start, end, color):
                        moves.append((start, end))
        return moves

    def make_move(self, start: Position, end: Position) -> bool:
        if self.state is not GameState.ACTIVE or not self.is_legal_move(start, end):
            return False

        piece = self.board.piece_at(start)
        assert piece is not None
        mover = self.turn
        captured = self.board.move(start, end)
        self.turn = mover.opponent
        gave_check = self.is_in_check(self.turn)

        self.history.append(
            MoveRecord(
                mover=mover,
                piece=piece.kind,
                start=start,
                end=end,
                captured=captured.kind if captured else None,
                gave_check=gave_check,
            )
        )

        if not self.legal_moves(self.turn):
            self.state = GameState.RED_WON if mover is Color.RED else GameState.BLACK_WON
        return True

    def to_dict(self) -> dict[str, object]:
        return {
            "version": 1,
            "board": self.board.to_dict(),
            "turn": self.turn.value,
            "state": self.state.value,
            "history": [move.to_dict() for move in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Game":
        try:
            if data.get("version") != 1:
                raise ValueError("Unsupported save version.")
            board_data = data["board"]
            history_data = data.get("history", [])
            if not isinstance(board_data, dict) or not isinstance(history_data, list):
                raise ValueError("Invalid game data.")
            game = cls(
                board=Board.from_dict(board_data),
                turn=Color(str(data["turn"])),
                state=GameState(str(data["state"])),
                history=[
                    MoveRecord.from_dict(item)
                    for item in history_data
                    if isinstance(item, dict)
                ],
            )
            if len(game.history) != len(history_data):
                raise ValueError("Invalid move history.")
            return game
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, ValueError):
                raise
            raise ValueError("Invalid game data.") from error

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, value: str) -> "Game":
        try:
            data = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("Invalid JSON game data.") from error
        if not isinstance(data, dict):
            raise ValueError("Game JSON must contain an object.")
        return cls.from_dict(data)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Game":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def status(self) -> str:
        if self.state is GameState.RED_WON:
            return "Red won"
        if self.state is GameState.BLACK_WON:
            return "Black won"
        check = " - check" if self.is_in_check(self.turn) else ""
        return f"{self.turn.value.capitalize()} to move{check}"
