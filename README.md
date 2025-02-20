# Notes

## Things to add/change

- Add castling options and tests
  - Ensure that castling options are removed when moving the King or Rooks
  - When allowing castling move, check that none of the squares in between will be in check
- Use the GameStatus.king_positions dictionary for checking for in check/checkmate
- Think about moving some logic to the Rules.py file. This will be things like Castling/En Passant logic
