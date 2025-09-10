#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_app_runs(self):
        at = AppTest.from_file("app.py")
        at.run()
        assert not at.exception
   
    def test_elements_appear(self):
        #This test was generated with help by Gemini, still, its not really passing, im not too sure why
        at = AppTest.from_file("app.py")
        at.run()

        self.assertTrue(at.subheader[0].exists())
        self.assertTrue(at.title[0].exists())
        self.assertTrue(at.image[0].exists())
        self.assertTrue(at.subheader[0].divider == "green")
        self.assertTrue(at.title[0].color == "red")


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
