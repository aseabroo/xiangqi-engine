import pytest

from xiangqi import Board, Color, Game, GameState, Piece, PieceType, Position


def p(row, col):
    return Position(row, col)


def test_initial_position_has_32_pieces():
    board = Board.initial()
    assert len(board.pieces) == 32
    assert board.piece_at(p(9, 4)) == Piece(Color.RED, PieceType.GENERAL)
    assert board.piece_at(p(0, 4)) == Piece(Color.BLACK, PieceType.GENERAL)


def test_position_parser_round_trip():
    position = Position.parse("e9")
    assert position == p(9, 4)
    assert str(position) == "e9"


def test_rook_requires_clear_path():
    board = Board({p(5, 4): Piece(Color.RED, PieceType.ROOK), p(3, 4): Piece(Color.RED, PieceType.SOLDIER)})
    assert not board.piece_rule_allows(p(5, 4), p(1, 4))
    board.pieces.pop(p(3, 4))
    assert board.piece_rule_allows(p(5, 4), p(1, 4))


def test_cannon_capture_requires_exactly_one_screen():
    cannon = Piece(Color.RED, PieceType.CANNON)
    target = Piece(Color.BLACK, PieceType.ROOK)
    screen = Piece(Color.RED, PieceType.SOLDIER)

    board = Board({p(7, 1): cannon, p(0, 1): target})
    assert not board.piece_rule_allows(p(7, 1), p(0, 1))

    board.pieces[p(4, 1)] = screen
    assert board.piece_rule_allows(p(7, 1), p(0, 1))

    board.pieces[p(2, 1)] = Piece(Color.BLACK, PieceType.SOLDIER)
    assert not board.piece_rule_allows(p(7, 1), p(0, 1))


def test_cannon_non_capture_cannot_jump():
    board = Board({
        p(7, 1): Piece(Color.RED, PieceType.CANNON),
        p(5, 1): Piece(Color.RED, PieceType.SOLDIER),
    })
    assert not board.piece_rule_allows(p(7, 1), p(3, 1))


def test_horse_leg_can_be_blocked():
    board = Board({p(4, 4): Piece(Color.RED, PieceType.HORSE)})
    assert board.piece_rule_allows(p(4, 4), p(2, 5))
    board.pieces[p(3, 4)] = Piece(Color.RED, PieceType.SOLDIER)
    assert not board.piece_rule_allows(p(4, 4), p(2, 5))


def test_elephant_cannot_cross_river_and_eye_can_be_blocked():
    board = Board({p(9, 2): Piece(Color.RED, PieceType.ELEPHANT)})
    assert board.piece_rule_allows(p(9, 2), p(7, 4))
    board.pieces[p(8, 3)] = Piece(Color.RED, PieceType.SOLDIER)
    assert not board.piece_rule_allows(p(9, 2), p(7, 4))

    board = Board({p(5, 2): Piece(Color.RED, PieceType.ELEPHANT)})
    assert not board.piece_rule_allows(p(5, 2), p(3, 4))


def test_general_and_advisor_stay_in_palace():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(9, 3): Piece(Color.RED, PieceType.ADVISOR),
    })
    assert board.piece_rule_allows(p(9, 4), p(8, 4))
    assert not board.piece_rule_allows(p(9, 4), p(9, 2))
    assert board.piece_rule_allows(p(9, 3), p(8, 4))
    assert not board.piece_rule_allows(p(9, 3), p(8, 2))


def test_soldier_gains_sideways_move_after_crossing_river():
    board = Board({p(6, 4): Piece(Color.RED, PieceType.SOLDIER)})
    assert board.piece_rule_allows(p(6, 4), p(5, 4))
    assert not board.piece_rule_allows(p(6, 4), p(6, 5))

    board = Board({p(4, 4): Piece(Color.RED, PieceType.SOLDIER)})
    assert board.piece_rule_allows(p(4, 4), p(4, 5))
    assert not board.piece_rule_allows(p(4, 4), p(5, 4))


def test_flying_generals_attack_each_other():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
    })
    game = Game(board)
    assert game.is_in_check(Color.RED)
    assert game.is_in_check(Color.BLACK)


def test_piece_between_generals_blocks_flying_attack():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(5, 4): Piece(Color.RED, PieceType.SOLDIER),
    })
    game = Game(board)
    assert not game.is_in_check(Color.RED)
    assert not game.is_in_check(Color.BLACK)


def test_move_exposing_flying_generals_is_illegal():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(5, 4): Piece(Color.RED, PieceType.ROOK),
    })
    game = Game(board, turn=Color.RED)
    assert not game.is_legal_move(p(5, 4), p(5, 5))


def test_move_that_does_not_resolve_check_is_illegal():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 3): Piece(Color.BLACK, PieceType.GENERAL),
        p(5, 4): Piece(Color.BLACK, PieceType.ROOK),
        p(9, 0): Piece(Color.RED, PieceType.ROOK),
    })
    game = Game(board, turn=Color.RED)
    assert game.is_in_check(Color.RED)
    assert not game.is_legal_move(p(9, 0), p(8, 0))


def test_turn_changes_after_legal_move():
    game = Game.new()
    assert game.make_move(p(6, 0), p(5, 0))
    assert game.turn is Color.BLACK


def test_wrong_color_cannot_move():
    game = Game.new()
    assert not game.make_move(p(3, 0), p(4, 0))


def test_capturing_general_ends_game():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(1, 4): Piece(Color.RED, PieceType.ROOK),
        p(5, 4): Piece(Color.BLACK, PieceType.SOLDIER),
    })
    game = Game(board, turn=Color.RED)
    # Move the rook laterally first so the board position is not an immediate flying-general check.
    board.pieces.pop(p(5, 4))
    board.pieces[p(5, 3)] = Piece(Color.BLACK, PieceType.SOLDIER)
    assert game.make_move(p(1, 4), p(0, 4))
    assert game.state is GameState.RED_WON


@pytest.mark.parametrize("bad", ["j0", "a:", "a10", "", "44"])
def test_invalid_coordinates_raise(bad):
    with pytest.raises(ValueError):
        Position.parse(bad)
