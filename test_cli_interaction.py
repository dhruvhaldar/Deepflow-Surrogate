"""
Tests for the CLI interaction logic in mesh_generation.py.
"""
import unittest
import os
from unittest.mock import patch
import mesh_generation

class TestMeshGenerationCLI(unittest.TestCase):
    """Tests for CLI interaction logic."""
    def setUp(self):
        self.test_file = "test_verify.msh"
        # Ensure file exists for some tests
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("dummy")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='y')
    def test_overwrite_yes_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (Yes)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> Yes")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)
        mock_input.assert_called_once()

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='n')
    def test_overwrite_no_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (No)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> No")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertFalse(result)
        mock_input.assert_called_once()

    @patch('sys.stdout.isatty', return_value=True)
    def test_overwrite_force_interactive(self, mock_isatty):
        """Test interactive overwrite with --force (should skip prompt)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite + Force")
        result = mesh_generation.check_overwrite(self.test_file, force=True)
        self.assertTrue(result)

    @patch('sys.stdout.isatty', return_value=False)
    def test_overwrite_non_interactive(self, mock_isatty):
        """Test non-interactive overwrite (should warn but proceed)"""
        # pylint: disable=unused-argument
        print("\nTesting: Non-interactive Overwrite")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)

    def test_new_file(self):
        """Test checking a non-existent file (should proceed)"""
        print("\nTesting: New File")
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
