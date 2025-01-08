"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test Commannds."""
    def test_wait_for_db_ready(self,patched_check):
        """Test waiting for database if database ready."""
        # patched_check in your test code is a mock object created by the @patch decorator, 
        # for the check method in the wait_for_db command
        # when we call check inside our command,inside our
        # test case ,we just want to return the True value
        patched_check.return_value = True
        # execute the inside wait_for_db
        call_command('wait_for_db')
        # It is used to assert that a mocked method or function was called exactly once with a specific set of arguments. 
        patched_check.assert_called_once_with(databases=['default'])

    # what should happen when database isnt ready
    # means check method returns some exceptions
    # that indicates database is not ready.
    @patch('time.sleep')
    def test_wait_for_db_delay(self,patched_sleep,patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [Psycopg2Error]*2 + \
            [OperationalError]*3 + [True]
        
        call_command('wait_for_db')

        # checking count of mock method
        self.assertEqual(patched_check.call_count,6)
        # to assert that a mock object (e.g., a method or function) was called at least once with the specified arguments
        patched_check.assert_called_with(databases=['default'])
