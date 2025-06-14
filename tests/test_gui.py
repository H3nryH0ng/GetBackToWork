import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from gui.overlay import Overlay
from gui.settings_window import SettingsWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.main_window = MainWindow()

    def test_window_title(self):
        self.assertEqual(self.main_window.windowTitle(), "GetB@ck2Work")

    def test_points_display(self):
        self.main_window.update_points(100)
        self.assertIn("100", self.main_window.points_label.text())

    def test_stats_display(self):
        self.main_window.update_stats({"productive_time": 120, "entertainment_time": 60})
        self.assertIn("120", self.main_window.stats_label.text())
        self.assertIn("60", self.main_window.stats_label.text())

class TestOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.overlay = Overlay()

    def test_overlay_visibility(self):
        self.overlay.show()
        self.assertTrue(self.overlay.isVisible())
        self.overlay.hide()
        self.assertFalse(self.overlay.isVisible())

    def test_message_display(self):
        test_message = "Test Message"
        self.overlay.show_message(test_message)
        self.assertIn(test_message, self.overlay.message_label.text())

class TestSettingsWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.settings_window = SettingsWindow()

    def test_settings_save(self):
        test_settings = {
            "point_rate": 1,
            "time_interval": 5,
            "blocking_level": "minimize"
        }
        self.settings_window.save_settings(test_settings)
        loaded_settings = self.settings_window.load_settings()
        self.assertEqual(loaded_settings, test_settings)

    def test_app_categories(self):
        test_categories = {
            "productive": ["app1", "app2"],
            "entertainment": ["game1", "game2"]
        }
        self.settings_window.save_app_categories(test_categories)
        loaded_categories = self.settings_window.load_app_categories()
        self.assertEqual(loaded_categories, test_categories)

if __name__ == '__main__':
    unittest.main() 