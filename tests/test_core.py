import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.point_system import PointSystem
from core.window_monitor import WindowMonitor
from core.app_controller import AppController
from core.data_manager import DataManager

class TestPointSystem(unittest.TestCase):
    def setUp(self):
        self.point_system = PointSystem()

    def test_initial_points(self):
        self.assertEqual(self.point_system.get_points(), 0)

    def test_add_points(self):
        self.point_system.add_points(10)
        self.assertEqual(self.point_system.get_points(), 10)

    def test_deduct_points(self):
        self.point_system.add_points(20)
        self.point_system.deduct_points(10)
        self.assertEqual(self.point_system.get_points(), 10)

    def test_daily_cap(self):
        self.point_system.add_points(150)  # Should cap at 100
        self.assertEqual(self.point_system.get_points(), 100)

class TestWindowMonitor(unittest.TestCase):
    def setUp(self):
        self.window_monitor = WindowMonitor()

    @patch('core.window_monitor.get_active_window')
    def test_get_active_window(self, mock_get_active_window):
        mock_get_active_window.return_value = "Test App"
        self.assertEqual(self.window_monitor.get_active_window(), "Test App")

class TestAppController(unittest.TestCase):
    def setUp(self):
        self.app_controller = AppController()

    def test_block_app(self):
        with patch('core.app_controller.psutil.process_iter') as mock_process_iter:
            mock_process = MagicMock()
            mock_process.name.return_value = "test_app.exe"
            mock_process_iter.return_value = [mock_process]
            
            self.app_controller.block_app("test_app.exe")
            mock_process.terminate.assert_called_once()

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.data_manager = DataManager()

    def test_save_load_data(self):
        test_data = {"points": 100, "apps": ["app1", "app2"]}
        self.data_manager.save_data(test_data)
        loaded_data = self.data_manager.load_data()
        self.assertEqual(loaded_data, test_data)

if __name__ == '__main__':
    unittest.main() 