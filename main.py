from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from ui.board import ChessBoard
from ui.move_history import MoveHistoryWidget
from chess_game.game import GameState
from utils.notation import to_algebraic_notation
import sys


class ChessApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("PyQt6 Chess")
        # Window size (x, y, width, height)
        self.setGeometry(100, 100, 1000, 800)

        # Main widget and layout for the window
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout(self.mainWidget)

        # Create a horizontal layout for board and move history
        self.board_and_history_layout = QHBoxLayout()

        # Create and add the ChessBoard widget
        self.chessBoard = ChessBoard()
        self.chessBoard.move_made.connect(self.update_move_history)
        self.board_and_history_layout.addWidget(self.chessBoard)

        # Add move history panel, stretching it to fill available height
        self.move_history_widget = MoveHistoryWidget()
        self.move_history_widget.setFixedWidth(200)
        self.board_and_history_layout.addWidget(self.move_history_widget)

        self.layout.addLayout(self.board_and_history_layout)

        # Add buttons, labels, etc. here
        self.button_layout = QHBoxLayout()
        self.printBoardButton = QPushButton("Print Board", self)
        self.printBoardButton.clicked.connect(self.print_board)
        self.button_layout.addWidget(self.printBoardButton)
        self.inCheckButton = QPushButton("Anyone in check?", self)
        self.inCheckButton.clicked.connect(self.print_in_check)
        self.button_layout.addWidget(self.inCheckButton)
        self.resetButton = QPushButton("Reset Game", self)
        self.resetButton.clicked.connect(self.reset_game)
        self.button_layout.addWidget(self.resetButton)

        self.layout.addLayout(self.button_layout)

    def update_move_history(self):
        """Refresh the move history display after each move."""
        move_list = [to_algebraic_notation(
            m, self.chessBoard.game_state) for m in self.chessBoard.game_state.history]
        self.move_history_widget.update_moves(move_list)

    def print_board(self):
        self.chessBoard.print_board()

    def print_in_check(self):
        self.chessBoard.print_in_check()

    def reset_game(self):
        """Show a confirmation dialog and reset the game if confirmed."""
        reply = QMessageBox.question(
            self, "Reset Game", "Are you sure you want to reset the game?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.chessBoard.reset_board()
            self.move_history_widget.update_moves([])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChessApp()
    window.show()
    sys.exit(app.exec())
