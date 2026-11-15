import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kde_window_size_screenshot.capture import Snapshot, WindowCapture, save_png
from kde_window_size_screenshot.environment import Check, CheckState, capture_block_reason, inspect_environment


class CaptureRegressionTests(unittest.TestCase):
    def test_x11_with_required_tools_has_no_confirmation_gate(self):
        display = Check('DISPLAY connection', CheckState.PASS, ':0')
        with patch('kde_window_size_screenshot.environment._check_display', return_value=display), \
             patch('kde_window_size_screenshot.environment.shutil.which', side_effect=lambda name: '/usr/bin/' + name), \
             patch('kde_window_size_screenshot.environment.os.access', return_value=True):
            self.assertEqual(capture_block_reason('xcb'), '')
            checks = inspect_environment('xcb')
            self.assertTrue(all(check.ok for check in checks))
            self.assertNotIn('Isolated display safety gate', [check.name for check in checks])

    def test_missing_xwd_is_reported_as_dependency(self):
        display = Check('DISPLAY connection', CheckState.PASS, ':0')
        with patch('kde_window_size_screenshot.environment._check_display', return_value=display), \
             patch('kde_window_size_screenshot.environment.shutil.which', side_effect=lambda name: None if name == 'xwd' else '/usr/bin/' + name), \
             patch('kde_window_size_screenshot.environment.os.access', return_value=True):
            self.assertIn('xwd', capture_block_reason('xcb'))

    def test_kwin_restores_fullscreen_after_maximization(self):
        saved = Snapshot('0x123', 2560, 0, 1920, 1080,
                         ['fullscreen', 'maximized_vert', 'maximized_horz'])
        calls = []
        def command(*args, **kwargs):
            calls.append(args)
            return ''
        with patch('kde_window_size_screenshot.capture.run', side_effect=command), \
             patch('kde_window_size_screenshot.capture.extents', return_value=(0, 0, 0, 0)), \
             patch('kde_window_size_screenshot.capture.geometry', return_value=(2560, 0, 1920, 1080)), \
             patch('kde_window_size_screenshot.capture.property_text', return_value='_NET_WM_STATE_FULLSCREEN, _NET_WM_STATE_MAXIMIZED_VERT, _NET_WM_STATE_MAXIMIZED_HORZ'), \
             patch('kde_window_size_screenshot.capture.time.sleep'):
            WindowCapture(Path('/unused')).restore(saved)
        added = [args[-1] for args in calls if args[-1].startswith('add,')]
        self.assertEqual(added[-1], 'add,fullscreen')

    def test_restore_allows_slow_chrome_resize(self):
        saved = Snapshot('0x123', 0, 0, 1920, 1036, [])
        with patch('kde_window_size_screenshot.capture.run'), \
             patch('kde_window_size_screenshot.capture.extents', return_value=(0, 0, 0, 0)), \
             patch('kde_window_size_screenshot.capture.geometry', return_value=(0, 0, 1920, 1036)), \
             patch('kde_window_size_screenshot.capture.property_text', return_value=''), \
             patch('kde_window_size_screenshot.capture.time.sleep'), \
             patch.object(WindowCapture, 'wait_size') as wait_size:
            WindowCapture(Path('/unused')).restore(saved)
        wait_size.assert_called_once_with('0x123', 1920, 1036, timeout=8)

    def test_output_does_not_overwrite_or_escape_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch('kde_window_size_screenshot.capture.time.strftime', return_value='fixed'):
                first = save_png(root, '../../window', b'first')
                second = save_png(root, '../../window', b'second')
            self.assertEqual(first.parent, root)
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), b'first')
            self.assertEqual(second.read_bytes(), b'second')


if __name__ == '__main__':
    unittest.main()
