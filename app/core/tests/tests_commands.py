"""
Test custom Django management commands.
"""

# Mock the behavior of database.
from unittest.mock import patch

# One possible error we get while we connect to database before it's ready.
from psycopg2 import OperationalError as Psycopg2Error

# Provided by Django to simulate or actually call a command by the name.
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Django BaseCommand has a method: check, and we're going to mock it.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        # We're going to use patched_check to customize the behavior.
        patched_check.return_value = True
        call_command('wait_for_db')

        # This check our mock command is called with
        # these parameters(database=['default'])
        patched_check.assert_called_once_with(databases=['default'])

    """
    Note: Orders matter!!! Mocks would be mapped from inside to outside
    For example: time.sleep -> first arg, cause it's inside
                 check -> second arg
    """
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""

        """
        Explanation:
            The first two times we called the mocked method,
            we want to raise Psycopg2Error.
            Then next three times raise OperationalError

        Here We will raise two different exception for different stage of
        database setup.
            Psycopg2Error:      Database hasn't set up, unable to be connected
            OperationalError:   Ready to be connected, but hasn't set up
                                testing database
        """
        # Makes it raise an exception instead of return a value.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # 6 = 2 + 3 + 1
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
