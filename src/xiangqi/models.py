from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Color(str, Enum):
    RED = "red"
    BLACK = "black"

    @property
    def opponent(self) -> "Color":
        return Color.BLACK if self is Color.RED else Color.RED


class PieceType(str, Enum):
    GENERAL = "general"
    ADVISOR = "advisor"
    ELEPHANT = "elephant"
    HORSE = "horse"
    ROOK = "rook"
    CANNON = "cannon"
    SOLDIER = "soldier"


@dataclass(frozen=True, slots=True)
class Position:
    row: int
    col: int

    def __post_init__(self) -> None:
        if not (0 <= self.row <= 9 and 0 <= self.col <= 8):
            raise ValueError(f"Position out of bounds: ({self.row}, {self.col})")

    @classmethod
    def parse(cls, value: str) -> "Position":
        value = value.strip().lower()
        if len(value) != 2 or value[0] not in "abcdefghi" or value[1] not in "0123456789":
            raise ValueError("Use coordinates a0 through i9.")
        return cls(row=int(value[1]), col=ord(value[0]) - ord("a"))

    def __str__(self) -> str:
        return f"{chr(ord('a') + self.col)}{self.row}"


@dataclass(frozen=True, slots=True)
class Piece:
    color: Color
    kind: PieceType

    @property
    def symbol(self) -> str:
        symbols = {
            PieceType.GENERAL: "G",
            PieceType.ADVISOR: "A",
            PieceType.ELEPHANT: "E",
            PieceType.HORSE: "H",
            PieceType.ROOK: "R",
            PieceType.CANNON: "C",
            PieceType.SOLDIER: "S",
        }
        symbol = symbols[self.kind]
        return symbol if self.color is Color.RED else symbol.lower()


@dataclass(frozen=True, slots=True)
class MoveRecord:
    mover: Color
    piece: PieceType
    start: Position
    end: Position
    captured: PieceType | None = None
    gave_check: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "mover": self.mover.value,
            "piece": self.piece.value,
            "start": str(self.start),
            "end": str(self.end),
            "captured": self.captured.value if self.captured else None,
            "gave_check": self.gave_check,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MoveRecord":
        try:
            captured = data.get("captured")
            return cls(
                mover=Color(str(data["mover"])),
                piece=PieceType(str(data["piece"])),
                start=Position.parse(str(data["start"])),
                end=Position.parse(str(data["end"])),
                captured=PieceType(str(captured)) if captured is not None else None,
                gave_check=bool(data.get("gave_check", False)),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Invalid move-history record.") from error
