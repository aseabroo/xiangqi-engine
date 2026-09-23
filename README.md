# Xiangqi Engine

A modern, test-driven Xiangqi (Chinese chess) engine in Python.

This project is a ground-up rebuild of a 2020 coursework project. The original implementation is preserved separately in `python-learning-archive`; this repository focuses on clearer architecture, explicit game state, complete move validation, and regression tests for difficult rules.

## Why this rebuild exists

The earlier version was a substantial learning project, but it mixed board mutation, move generation, and rule enforcement in ways that made bugs difficult to isolate. This version separates those concerns and treats edge cases as tests first.

## Current features

- Standard 9 x 10 Xiangqi board and starting position
- General, advisor, elephant, horse, rook, cannon, and soldier movement
- Palace and river restrictions
- Horse-leg and elephant-eye blocking
- Cannon screen rules
- Flying-general rule
- Check detection
- Rejection of moves that leave your own general in check
- Checkmate/stalemate detection
- Simple coordinate-based CLI
- Pytest regression suite

## Project layout

```text
src/xiangqi/
    board.py      board state and piece-level move rules
    game.py       turns, check, legal moves, and game state
    models.py     immutable domain types
    cli.py        small playable command-line interface
tests/
    test_engine.py
```

## Install and test

```bash
python -m pip install -e ".[dev]"
pytest
```

Run the CLI:

```bash
xiangqi
```

Coordinates use algebraic-style files `a-i` and ranks `0-9`. For example:

```text
a9 a8
```

## Scope and known limitation

Core board movement, check, self-check, checkmate, and stalemate-as-loss are implemented. Tournament-specific repetition and perpetual-check adjudication are not yet implemented; those rules require move-history policy beyond basic board legality.

## Engineering goals

This is intentionally an engine first. The priorities are deterministic state transitions, rules that can be tested independently, and a domain model that can later support a web UI, move notation, persistence, or computer play without rewriting the core.

## Provenance

The concept comes from my 2020 Python coursework project, but this repository is a new implementation rather than a cleaned-up copy. The historical source remains in `aseabroo/python-learning-archive` for comparison and provenance.
