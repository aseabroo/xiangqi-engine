from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .board import Board
from .models import Color, PieceType, Position


class GameState(str, Enum):
    ACTIVE = "active"
    RED_WON = "red_won"
    BLACK_WON = "black_won"


@dataclass
class Game:
    board: Board
    turn: Color = Color.RED
    state: GameState = GameState.ACTIVE

    @classmethod
    def new(cls) -> "Game":
        return cls(Board.initial())

    def is_in_check(self, color: Color, board: Board | None = None) -> bool:
        board = board or self.board
        general = board.general_position(color)
        if general is None:
            return True

        for start, piece in board.pieces.items():
            if piece.color is color.opponent and board.piece_rule_allows(start, general, attack=True):
                return True
        return False

    def is_legal_move(self, start: Position, end: Position, color: Color | None = None) -> bool:
        color = color or self.turn
        piece = self.board.piece_at(start)
        if piece is None or piece.color is not color:
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

        captured = self.board.move(start, end)
        mover = self.turn

        if captured is not None and captured.kind is PieceType.GENERAL:
            self.state = GameState.RED_WON if mover is Color.RED else GameState.BLACK_WON
            return True

        self.turn = mover.opponent
        if not self.legal_moves(self.turn):
            self.state = GameState.RED_WON if mover is Color.RED else GameState.BLACK_WON
        return True

    def status(self) -> str:
        if self.state is GameState.RED_WON:
            return "Red won"
        if self.state is GameState.BLACK_WON:
            return "Black won"
        check = " - check" if self.is_in_check(self.turn) else ""
        return f"{self.turn.value.capitalize()} to move{check}"
