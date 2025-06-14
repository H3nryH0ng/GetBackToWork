import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.system_utils import SystemUtils
from utils.notifications import NotificationManager

class TestSystemUtils(unittest.TestCase):
    def setUp(self):
        self.system_utils = SystemUtils()

    @patch('utils.system_utils.ctypes.windll.shell32.IsUserAnAdmin')
    def test_admin_check(self, mock_is_admin):
        mock_is_admin.return_value = True
        self.assertTrue(self.system_utils.is_admin())

        mock_is_admin.return_value = False
        self.assertFalse(self.system_utils.is_admin())

    @patch('utils.system_utils.winreg.OpenKey')
    @patch('utils.system_utils.winreg.SetValueEx')
    def test_set_startup(self, mock_set_value, mock_open_key):
        self.system_utils.set_startup(True)
        mock_set_value.assert_called_once()

    @patch('utils.system_utils.winreg.OpenKey')
    @patch('utils.system_utils.winreg.DeleteValue')
    def test_remove_startup(self, mock_delete_value, mock_open_key):
        self.system_utils.set_startup(False)
        mock_delete_value.assert_called_once()

class TestNotificationManager(unittest.TestCase):
    def setUp(self):
        self.notification_manager = NotificationManager()

    def test_notification_queue(self):
        self.notification_manager.queue_notification("Test Title", "Test Message")
        self.assertEqual(len(self.notification_manager.notification_queue), 1)
        self.assertEqual(self.notification_manager.notification_queue[0]["title"], "Test Title")
        self.assertEqual(self.notification_manager.notification_queue[0]["message"], "Test Message")

    @patch('utils.notifications.NotificationManager.show_notification')
    def test_process_queue(self, mock_show):
        self.notification_manager.queue_notification("Test Title", "Test Message")
        self.notification_manager.process_queue()
        mock_show.assert_called_once_with("Test Title", "Test Message")

    def test_notification_settings(self):
        test_settings = {
            "enabled": True,
            "sound": True,
            "duration": 5
        }
        self.notification_manager.save_settings(test_settings)
        loaded_settings = self.notification_manager.load_settings()
        self.assertEqual(loaded_settings, test_settings)

    @patch('utils.notifications.NotificationManager.show_notification')
    def test_productivity_notification(self, mock_show):
        self.notification_manager.show_productivity_notification(100)
        mock_show.assert_called_once()
        self.assertIn("100", mock_show.call_args[0][1])

    @patch('utils.notifications.NotificationManager.show_notification')
    def test_points_notification(self, mock_show):
        self.notification_manager.show_points_notification(50)
        mock_show.assert_called_once()
        self.assertIn("50", mock_show.call_args[0][1])

if __name__ == '__main__':
    unittest.main() 