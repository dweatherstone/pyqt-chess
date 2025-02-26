from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from chess_game.pieces import Queen, Rook, Bishop, Knight


class PromotionDialog(QDialog):
    def __init__(self, parent=None, colour=None):
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        # Makes this dialog block interactions with the main window
        self.setModal(True)
        self.setFixedSize(500, 200)

        self.selected_piece = None  # Store the selected piece type

        # Layout
        layout = QVBoxLayout(self)
        label = QLabel("Choose a piece for promotion:")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Create buttons with images for each promotion option
        self.pieces = {
            "Queen": Queen(colour, 0, 0),
            "Rook": Rook(colour, 0, 0),
            "Bishop": Bishop(colour, 0, 0),
            "Knight": Knight(colour, 0, 0)
        }

        for name, piece in self.pieces.items():
            btn = QPushButton()
            btn.setIcon(QIcon(piece.get_pixmap()))
            btn.setIconSize(piece.get_pixmap().size())
            btn.setFixedSize(100, 100)
            btn.setStyleSheet(
                "QPushButton { border: 2px solid black; }")
            # Capture piece type
            btn.clicked.connect(lambda checked, p=name: self.select_piece(p))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        # Closes dialog without selection
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def select_piece(self, piece_name):
        """Set the selected piece type and close dialog."""
        self.selected_piece = piece_name
        self.accept()

    def get_selected_piece(self):
        """Return the chosen piece type."""
        return self.selected_piece
