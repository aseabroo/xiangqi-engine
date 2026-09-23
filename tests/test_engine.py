import pytest

from xiangqi import Board, Color, Game, GameState, MoveRecord, Piece, PieceType, Position


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


def test_general_is_not_capturable():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(1, 4): Piece(Color.RED, PieceType.ROOK),
        p(5, 4): Piece(Color.BLACK, PieceType.SOLDIER),
    })
    game = Game(board, turn=Color.RED)
    assert not game.is_legal_move(p(1, 4), p(0, 4))


def test_checkmate_ends_game_without_general_capture():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(2, 4): Piece(Color.RED, PieceType.ROOK),
        p(1, 3): Piece(Color.RED, PieceType.ROOK),
        p(1, 5): Piece(Color.RED, PieceType.ROOK),
    })
    game = Game(board, turn=Color.RED)
    assert game.make_move(p(2, 4), p(1, 4))
    assert game.is_in_check(Color.BLACK)
    assert game.legal_moves(Color.BLACK) == []
    assert game.state is GameState.RED_WON


def test_stalemate_is_a_loss_in_xiangqi():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(5, 4): Piece(Color.RED, PieceType.SOLDIER),
        p(1, 3): Piece(Color.RED, PieceType.ROOK),
        p(1, 5): Piece(Color.RED, PieceType.ROOK),
        p(5, 2): Piece(Color.RED, PieceType.HORSE),
    })
    game = Game(board, turn=Color.RED)
    assert game.make_move(p(5, 2), p(3, 3))
    assert not game.is_in_check(Color.BLACK)
    assert game.legal_moves(Color.BLACK) == []
    assert game.state is GameState.RED_WON


@pytest.mark.parametrize("bad", ["j0", "a:", "a10", "", "44"])
def test_invalid_coordinates_raise(bad):
    with pytest.raises(ValueError):
        Position.parse(bad)


def test_move_history_records_check_and_capture():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 3): Piece(Color.BLACK, PieceType.GENERAL),
        p(5, 4): Piece(Color.RED, PieceType.ROOK),
        p(5, 3): Piece(Color.BLACK, PieceType.SOLDIER),
    })
    game = Game(board, turn=Color.RED)
    assert game.make_move(p(5, 4), p(5, 3))
    record = game.history[-1]
    assert record == MoveRecord(
        mover=Color.RED,
        piece=PieceType.ROOK,
        start=p(5, 4),
        end=p(5, 3),
        captured=PieceType.SOLDIER,
        gave_check=True,
    )


def test_game_json_round_trip_preserves_state_and_history():
    game = Game.new()
    assert game.make_move(p(6, 0), p(5, 0))
    assert game.make_move(p(3, 0), p(4, 0))

    restored = Game.from_json(game.to_json())
    assert restored.turn is game.turn
    assert restored.state is game.state
    assert restored.board.pieces == game.board.pieces
    assert restored.history == game.history


def test_save_and_load_round_trip(tmp_path):
    game = Game.new()
    assert game.make_move(p(6, 2), p(5, 2))
    path = tmp_path / "game.json"
    game.save(path)

    restored = Game.load(path)
    assert restored.to_dict() == game.to_dict()


def test_board_validation_rejects_missing_general():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
    })
    with pytest.raises(ValueError, match="Missing black general"):
        board.validate()


def test_board_validation_rejects_general_outside_palace():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(3, 4): Piece(Color.BLACK, PieceType.GENERAL),
    })
    with pytest.raises(ValueError, match="outside the palace"):
        board.validate()


def test_board_validation_rejects_too_many_piece_types():
    board = Board({
        p(9, 4): Piece(Color.RED, PieceType.GENERAL),
        p(0, 4): Piece(Color.BLACK, PieceType.GENERAL),
        p(8, 0): Piece(Color.RED, PieceType.ROOK),
        p(8, 1): Piece(Color.RED, PieceType.ROOK),
        p(8, 2): Piece(Color.RED, PieceType.ROOK),
    })
    with pytest.raises(ValueError, match="Too many red rooks"):
        board.validate()


def test_deserialization_rejects_duplicate_positions():
    data = Board.initial().to_dict()
    pieces = data["pieces"]
    pieces.append(dict(pieces[0]))
    with pytest.raises(ValueError, match="Duplicate board position"):
        Board.from_dict(data)
