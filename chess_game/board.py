from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from chess_game.game import GameState


class ChessBoard(QWidget):
    def __init__(self, game_state: GameState):
        super().__init__()

        # Store reference to game logic
        self.game_state = game_state

        # Set up the layout of the board
        self.gridLayoutBoard = QGridLayout(self)
        self.gridLayoutBoard.setSpacing(0)

        self.labels = [[QLabel(self) for _ in range(8)] for _ in range(8)]
        self.selected_piece = None  # Track selected piece
        self.valid_moves = []  # Track valid moves for highlighting

        self.setup_chessboard()

    def setup_chessboard(self):
        """Draws the board and pieces based on `self.game_state` state."""
        for row in range(8):
            for col in range(8):
                label = self.labels[row][col]
                label.setFixedSize(75, 75)
                label.setStyleSheet(self.get_square_style(row, col))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.gridLayoutBoard.addWidget(label, row, col)

                # If there's a piece in this position, set its image
                piece = self.game_state.board[row][col]
                if piece:
                    label.setPixmap(piece.get_pixmap())

    def get_square_style(self, row: int, col: int, highlight: bool = False) -> str:
        """Returns the CSS style for a board square."""
        base_colour = "#DDB88C" if (row + col) % 2 == 0 else "#A66F4F"
        highlight_colour = "#77DD77"  # Light green for highlighting valid moves
        return f"background-color: {highlight_colour if highlight else base_colour};"

    def highlight_squares(self, squares: list) -> None:
        pass

    def mousePressEvent(self, event: QMouseEvent) -> None:
        return super().mousePressEvent(event)

    def mark_selection(self, row: int, col: int) -> None:
        pass

    def clear_selection(self) -> None:
        pass
