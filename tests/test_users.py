import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
import lnto
import tests.db
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.tags import Tag

class TestLinks(unittest.TestCase):
    
    def setUp(self):
        tests.db.init_test_db()
    
    def tearDown(self):
        tests.db.delete_test_db()
    
    def test_get_by_username_exists(self):
        usr = User.get_by_username('testuser')
        self.assertEqual(usr.username, 'testuser')
    
    def test_get_by_username_nonexistent(self):
        usr = User.get_by_username('thisuserdoesnotexist')
        self.assertEqual(usr, None)
    
if __name__ == '__main__':
    unittest.main()