from __future__ import annotations

from dataclasses import dataclass, field

from .models import Color, Piece, PieceType, Position


@dataclass
class Board:
    pieces: dict[Position, Piece] = field(default_factory=dict)

    @classmethod
    def initial(cls) -> "Board":
        board = cls()
        back_rank = [
            PieceType.ROOK,
            PieceType.HORSE,
            PieceType.ELEPHANT,
            PieceType.ADVISOR,
            PieceType.GENERAL,
            PieceType.ADVISOR,
            PieceType.ELEPHANT,
            PieceType.HORSE,
            PieceType.ROOK,
        ]
        for col, kind in enumerate(back_rank):
            board.pieces[Position(0, col)] = Piece(Color.BLACK, kind)
            board.pieces[Position(9, col)] = Piece(Color.RED, kind)

        for col in (1, 7):
            board.pieces[Position(2, col)] = Piece(Color.BLACK, PieceType.CANNON)
            board.pieces[Position(7, col)] = Piece(Color.RED, PieceType.CANNON)

        for col in (0, 2, 4, 6, 8):
            board.pieces[Position(3, col)] = Piece(Color.BLACK, PieceType.SOLDIER)
            board.pieces[Position(6, col)] = Piece(Color.RED, PieceType.SOLDIER)
        return board

    def copy(self) -> "Board":
        return Board(self.pieces.copy())

    def piece_at(self, position: Position) -> Piece | None:
        return self.pieces.get(position)

    def move(self, start: Position, end: Position) -> Piece | None:
        piece = self.pieces.pop(start)
        captured = self.pieces.pop(end, None)
        self.pieces[end] = piece
        return captured

    def general_position(self, color: Color) -> Position | None:
        for position, piece in self.pieces.items():
            if piece.color is color and piece.kind is PieceType.GENERAL:
                return position
        return None

    def path_count(self, start: Position, end: Position) -> int:
        if start.row == end.row:
            step = 1 if end.col > start.col else -1
            return sum(
                Position(start.row, col) in self.pieces
                for col in range(start.col + step, end.col, step)
            )
        if start.col == end.col:
            step = 1 if end.row > start.row else -1
            return sum(
                Position(row, start.col) in self.pieces
                for row in range(start.row + step, end.row, step)
            )
        raise ValueError("Path count requires an orthogonal move.")

    def piece_rule_allows(self, start: Position, end: Position) -> bool:
        piece = self.piece_at(start)
        if piece is None or start == end:
            return False

        target = self.piece_at(end)
        if target is not None and target.color is piece.color:
            return False

        dr = end.row - start.row
        dc = end.col - start.col
        adr, adc = abs(dr), abs(dc)

        if piece.kind is PieceType.GENERAL:
            if start.col == end.col and target is not None and target.kind is PieceType.GENERAL:
                return self.path_count(start, end) == 0
            palace_rows = range(7, 10) if piece.color is Color.RED else range(0, 3)
            return end.row in palace_rows and 3 <= end.col <= 5 and adr + adc == 1

        if piece.kind is PieceType.ADVISOR:
            palace_rows = range(7, 10) if piece.color is Color.RED else range(0, 3)
            return end.row in palace_rows and 3 <= end.col <= 5 and adr == 1 and adc == 1

        if piece.kind is PieceType.ELEPHANT:
            if adr != 2 or adc != 2:
                return False
            if piece.color is Color.RED and end.row < 5:
                return False
            if piece.color is Color.BLACK and end.row > 4:
                return False
            eye = Position(start.row + dr // 2, start.col + dc // 2)
            return self.piece_at(eye) is None

        if piece.kind is PieceType.HORSE:
            if sorted((adr, adc)) != [1, 2]:
                return False
            if adr == 2:
                leg = Position(start.row + (1 if dr > 0 else -1), start.col)
            else:
                leg = Position(start.row, start.col + (1 if dc > 0 else -1))
            return self.piece_at(leg) is None

        if piece.kind is PieceType.ROOK:
            return (start.row == end.row or start.col == end.col) and self.path_count(start, end) == 0

        if piece.kind is PieceType.CANNON:
            if start.row != end.row and start.col != end.col:
                return False
            screens = self.path_count(start, end)
            if target is None:
                return screens == 0
            return screens == 1

        if piece.kind is PieceType.SOLDIER:
            forward = -1 if piece.color is Color.RED else 1
            crossed = start.row <= 4 if piece.color is Color.RED else start.row >= 5
            if dr == forward and dc == 0:
                return True
            return crossed and dr == 0 and adc == 1

        return False

    def __str__(self) -> str:
        lines = ["    a b c d e f g h i"]
        for row in range(10):
            cells = [self.piece_at(Position(row, col)) for col in range(9)]
            lines.append(f"{row:>2}  " + " ".join(piece.symbol if piece else "." for piece in cells))
        return "\n".join(lines)
