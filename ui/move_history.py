from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from typing import List


class MoveHistoryWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.setLayout(self.layout)

    def update_moves(self, move_list: List[str]):
        """Update the move history display."""
        formatted_moves = ""
        for i in range(0, len(move_list), 2):
            move_number = (i // 2) + 1  # Move number starts from 1
            white_move = move_list[i]
            black_move = move_list[i + 1] if i + 1 < len(move_list) else ""

            formatted_moves += f"{move_number}. {white_move:<8} {black_move}\n"

        self.text_area.setPlainText(formatted_moves)
