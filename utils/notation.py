from chess_game.enums import PieceType
from chess_game.game import GameState
from chess_game.move import Move
from typing import List
import copy


def to_algebraic_notation(move: Move, game: GameState) -> str:
    """Convert a move to algebraic notation based on the current game state."""

    # First check for the special case of castling
    if move.castling:
        if move.castling == 'kingside':
            return 'O-O'
        elif move.castling == 'queenside':
            return 'O-O-O'

    piece_notation = {
        PieceType.PAWN: "",
        PieceType.KNIGHT: "N",
        PieceType.BISHOP: "B",
        PieceType.ROOK: "R",
        PieceType.QUEEN: "Q",
        PieceType.KING: "K"
    }

    # Basic move details
    piece = move.piece_type
    start_square = to_square_notation(move.from_row, move.from_col)
    end_square = to_square_notation(move.to_row, move.to_col)

    # Disambiguations: first get all possible moves of the same piece type as made this move
    all_moves = []
    for row in range(8):
        for col in range(8):
            p = game.board[row][col]
            if p and p.piece_type == piece and p.colour == game.turn:
                all_moves += [m for m in game.get_valid_moves(
                    row, col) if m.is_equal(move.to_row, move.to_col)]
    if len(all_moves) > 1:
        disambiguation_str = get_disambiguation_str(all_moves, move)
        move_str = f"{piece_notation.get(piece, '')}{disambiguation_str}"

    else:
        move_str = f"{piece_notation.get(piece, '')}"

    if move.captured_piece:
        if piece == PieceType.PAWN:
            move_str += start_square[0]
        move_str += 'x'
    elif move.en_passant:
        move_str += start_square[0] + 'x'

    move_str += f"{end_square}"

    if move.promotion:
        move_str += "=" + piece_notation.get(move.promotion, '')

    temp_game_copy = copy.deepcopy(game)
    temp_game_copy.move_piece(move)
    if temp_game_copy.is_checkmate:
        move_str += '#'
    elif temp_game_copy.in_check:
        move_str += '+'

    return move_str


def to_square_notation(row: int, col: int) -> str:
    """Convert a board square index (row, col) to argebraic notation (e.g. 'a8')."""
    file = chr(ord('a') + col)  # Convert column (0-7) to file ('a'-'h')
    rank = 8 - row
    return f"{file}{rank}"


def get_disambiguation_str(moves: List[Move], move: Move) -> str:
    """Handle disambiguation for moves of the same piece type."""
    possible_pieces = [(m.from_row, m.from_col) for m in moves]

    # Group pieces by files and ranks
    files = {col for _, col in possible_pieces}
    ranks = {row for row, _ in possible_pieces}

    start_square = to_square_notation(move.from_row, move.from_col)

    if len(files) > 1 and len(ranks) == 1:
        # Disambiguate by file: add the file (column) letter to the move
        return start_square[0]
    elif len(files) == 1 and len(ranks) > 1:
        # Disambiguate by rank: add the rank number to the move
        return start_square[1]
    else:
        # Double disambiguation
        return start_square
