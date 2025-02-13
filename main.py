from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from chess_game.board import ChessBoard
from chess_game.game import GameState
import sys


class ChessApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("PyQt6 Chess")
        # Window size (x, y, width, height)
        self.setGeometry(100, 100, 800, 800)

        # Main widget and layout for the window
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout(self.mainWidget)

        # Create and add the ChessBoard widget
        gs = GameState()
        self.chessBoard = ChessBoard(gs)
        self.layout.addWidget(self.chessBoard)

        # Add buttons, labels, etc. here
        self.printBoardButton = QPushButton("Print Board", self)
        self.printBoardButton.clicked.connect(gs.print_board)
        self.layout.addWidget(self.printBoardButton)
        self.inCheckButton = QPushButton("Anyone in check?", self)
        self.inCheckButton.clicked.connect(gs.print_in_check)
        self.layout.addWidget(self.inCheckButton)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChessApp()
    window.show()
    sys.exit(app.exec())
