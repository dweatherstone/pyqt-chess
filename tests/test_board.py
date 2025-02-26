from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys
import unittest
from ui.board import ChessBoard, PromotionDialog
from chess_game.enums import Colour


class TestPromotionDialog(unittest.TestCase):
    @classmethod
    def setUp(cls):
        """Create a QApplication instance if needed (PyQt requires it)"""
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_promotion_dialog_opens(self):
        """Ensure the promotion dialog appears when needed"""
        dialog = PromotionDialog(colour=Colour.WHITE)
        self.assertEqual(dialog.isVisible(), False)

        QTest.qWait(100)
        dialog.show()
        self.assertEqual(dialog.isVisible(), True)

        dialog.accept()

    def test_promotion_choice(self):
        """Simulate the user clicking on a piece button"""
        dialog = PromotionDialog(colour=Colour.WHITE)
        dialog.show()

        # Find the Queen button (assuming it's the first button in the layout)
        queen_button = dialog.findChildren(QPushButton)[0]

        QTest.mouseClick(queen_button, Qt.MouseButton.LeftButton)

        self.assertEqual(dialog.get_selected_piece(), "Queen")
