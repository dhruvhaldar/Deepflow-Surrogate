"""
Tests for the CLI interaction logic in mesh_generation.py.
"""
import unittest
import os
from io import StringIO
from unittest.mock import patch
import mesh_generation

class TestDirectoryCreation(unittest.TestCase):
    """Tests for directory creation logic."""

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    def test_directory_exists(self, mock_exists, mock_makedirs):
        """Test that nothing happens if directory exists."""
        # pylint: disable=unused-argument
        mesh_generation.ensure_directory_exists("existing_dir/file.msh")
        mock_makedirs.assert_not_called()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_directory_does_not_exist(self, mock_exists, mock_makedirs, mock_stdout):
        """Test that directory is created if it does not exist."""
        # pylint: disable=unused-argument
        # Note: os.path.dirname("new_dir/file.msh") -> "new_dir"
        mesh_generation.ensure_directory_exists("new_dir/file.msh")
        mock_makedirs.assert_called_with("new_dir", exist_ok=True)
        self.assertIn("Created directory 'new_dir'", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_directory_creation_fails(self, mock_exists, mock_makedirs, mock_stdout):
        """Test that script exits if directory creation fails."""
        # pylint: disable=unused-argument
        mock_makedirs.side_effect = OSError("Permission denied")
        with self.assertRaises(SystemExit) as cm:
            mesh_generation.ensure_directory_exists("root_dir/file.msh")
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Error creating directory 'root_dir'", mock_stdout.getvalue())

    @patch('os.makedirs')
    def test_no_output_file(self, mock_makedirs):
        """Test that function returns early if no filepath is provided."""
        mesh_generation.ensure_directory_exists(None)
        mock_makedirs.assert_not_called()

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
        print("\nTesting: Interactive Overwrite -> y")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)
        mock_input.assert_called_once()

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='yes')
    def test_overwrite_full_yes_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (full 'yes')"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> yes")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='YES')
    def test_overwrite_case_insensitive_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (case insensitive 'YES')"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> YES")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertTrue(result)

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='n')
    def test_overwrite_no_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (No)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> n")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertFalse(result)
        mock_input.assert_called_once()

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='NO')
    def test_overwrite_no_upper_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (NO)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> NO")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertFalse(result)

    @patch('sys.stdout.isatty', return_value=True)
    @patch('builtins.input', return_value='')
    def test_overwrite_empty_interactive(self, mock_input, mock_isatty):
        """Test interactive overwrite confirmation (Empty input)"""
        # pylint: disable=unused-argument
        print("\nTesting: Interactive Overwrite -> Empty")
        result = mesh_generation.check_overwrite(self.test_file, force=False)
        self.assertFalse(result)

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

class TestOutputPathValidation(unittest.TestCase):
    """Tests for output path validation."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_extension(self, mock_stdout):
        """Test that .msh is appended if extension is missing."""
        result = mesh_generation.validate_output_path("output_file")
        self.assertEqual(result, "output_file.msh")
        self.assertIn("Defaulting to 'output_file.msh'", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_valid_extension(self, mock_stdout):
        """Test that valid extension is unchanged."""
        result = mesh_generation.validate_output_path("output_file.msh")
        self.assertEqual(result, "output_file.msh")
        self.assertEqual(mock_stdout.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_suspicious_extension(self, mock_stdout):
        """Test that suspicious extension triggers a warning."""
        result = mesh_generation.validate_output_path("output_file.txt")
        self.assertEqual(result, "output_file.txt")
        self.assertIn("likely not supported", mock_stdout.getvalue())

    def test_none_filepath(self):
        """Test that None filepath is handled gracefully."""
        result = mesh_generation.validate_output_path(None)
        self.assertIsNone(result)

    @patch('sys.stdout', new_callable=StringIO)
    def test_directory_separator(self, mock_stdout):
        """Test that path ending in separator is treated as directory."""
        sep = os.sep
        path = f"some_dir{sep}"
        expected = os.path.join(path, "airfoil.msh")

        result = mesh_generation.validate_output_path(path)
        self.assertEqual(result, expected)
        self.assertIn("appears to be a directory", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('os.path.isdir', return_value=True)
    def test_existing_directory(self, mock_isdir, mock_stdout):
        """Test that existing directory is handled correctly."""
        path = "existing_dir"
        expected = os.path.join(path, "airfoil.msh")

        result = mesh_generation.validate_output_path(path)
        self.assertEqual(result, expected)
        self.assertIn("appears to be a directory", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('os.path.isdir', return_value=True)
    def test_dot_path(self, mock_isdir, mock_stdout):
        """Test that '.' is treated as directory."""
        result = mesh_generation.validate_output_path(".")
        expected = os.path.join(".", "airfoil.msh")
        self.assertEqual(result, expected)
        self.assertIn("appears to be a directory", mock_stdout.getvalue())

class TestSpinner(unittest.TestCase):
    """Tests for the Spinner class."""

    @patch('threading.Thread')
    def test_spinner_tty(self, mock_thread):
        """Test spinner behavior in TTY mode."""
        # pylint: disable=unused-argument
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            mock_stdout.isatty = lambda: True
            spinner = mesh_generation.Spinner("Testing...")
            with spinner:
                pass

            output = mock_stdout.getvalue()
            self.assertIn("\033[?25l", output, "Should hide cursor in TTY mode")
            self.assertIn("\033[?25h", output, "Should show cursor after spinner")

    def test_spinner_non_tty(self):
        """Test spinner behavior in non-TTY mode."""
        # pylint: disable=unused-argument
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            mock_stdout.isatty = lambda: False
            spinner = mesh_generation.Spinner("Testing...")
            with spinner:
                pass

            output = mock_stdout.getvalue()
            self.assertIn("Testing...", output, "Should print message in non-TTY mode")
            self.assertNotIn("\033[?25l", output, "Should NOT hide cursor in non-TTY mode")

    def test_spinner_non_tty_completion(self):
        """Test spinner completion feedback in non-TTY mode."""
        # pylint: disable=unused-argument
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            mock_stdout.isatty = lambda: False
            spinner = mesh_generation.Spinner("Testing...")
            with spinner:
                pass

            output = mock_stdout.getvalue()
            self.assertIn("Testing... ✅", output, "Should print completion feedback")

    def test_spinner_non_tty_failure(self):
        """Test spinner failure feedback in non-TTY mode."""
        # pylint: disable=unused-argument
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            mock_stdout.isatty = lambda: False
            spinner = mesh_generation.Spinner("Testing...")
            try:
                with spinner:
                    raise ValueError("Simulated error")
            except ValueError:
                pass

            output = mock_stdout.getvalue()
            self.assertIn("Testing... ❌", output, "Should print failure feedback")

class TestMeshStatistics(unittest.TestCase):
    """Tests for the mesh statistics output."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_output_format_with_file(self, mock_stdout):
        """Test that the output format includes element breakdown and tip when file is saved."""
        # Use a small number of points for speed
        points = mesh_generation.generate_airfoil_points(20)
        output_file = "test_stats.msh"

        try:
            # We don't need to actually write to disk for the logic test, but the function does.
            # We can let it write and then clean up.
            mesh_generation.generate_gmsh_mesh(points, output_file)

            output = mock_stdout.getvalue()
            self.assertIn("Mesh Statistics:", output)
            self.assertIn("Triangles:", output)
            self.assertIn("Quads:", output)
            self.assertIn(
                f"Tip: View the mesh using 'gmsh {output_file}'",
                output
            )

        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    @patch('sys.stdout', new_callable=StringIO)
    def test_output_format_without_file(self, mock_stdout):
        """
        Test that the output format includes element breakdown but NO tip
        when file is not saved.
        """
        points = mesh_generation.generate_airfoil_points(20)

        mesh_generation.generate_gmsh_mesh(points, None)

        output = mock_stdout.getvalue()
        self.assertIn("Mesh Statistics:", output)
        self.assertIn("Triangles:", output)
        self.assertIn("Quads:", output)
        self.assertNotIn("Tip: View the mesh", output)

class TestPreviewFlag(unittest.TestCase):
    """Tests for the --preview flag functionality."""

    @patch('mesh_generation.gmsh')
    @patch('sys.stdout', new_callable=StringIO)
    def test_preview_calls_fltk_run(self, mock_stdout, mock_gmsh):
        """Test that preview=True calls gmsh.fltk.run()."""
        # Mock environment to simulate display available
        with patch.dict(os.environ, {"DISPLAY": ":0"}), \
             patch('sys.stdout.isatty', return_value=True):

            # Use small points to run fast
            points = mesh_generation.generate_airfoil_points(10)

            mesh_generation.generate_gmsh_mesh(points, preview=True)

            # Verify gmsh.fltk.run was called
            mock_gmsh.fltk.run.assert_called_once()
            self.assertIn("Opening preview...", mock_stdout.getvalue())

    @patch('mesh_generation.gmsh')
    @patch('sys.stdout', new_callable=StringIO)
    def test_preview_skipped_no_display(self, mock_stdout, mock_gmsh):
        """Test that preview is skipped if no display is detected."""
        # Mock environment to simulate NO display
        # Remove DISPLAY if present
        env = os.environ.copy()
        if "DISPLAY" in env:
            del env["DISPLAY"]

        with patch.dict(os.environ, env, clear=True), \
             patch('sys.platform', "linux"), \
             patch('sys.stdout.isatty', return_value=True):

            points = mesh_generation.generate_airfoil_points(10)

            mesh_generation.generate_gmsh_mesh(points, preview=True)

            # Verify gmsh.fltk.run was NOT called
            mock_gmsh.fltk.run.assert_not_called()
            self.assertIn("Preview skipped", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
