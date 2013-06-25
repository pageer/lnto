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
    
    def test_get_by_name_exists(self):
        tag = Tag.get_by_name('test1')
        self.assertEqual(tag.tag_name, 'test1')
    
    def test_get_by_name_does_not_exist(self):
        tag = Tag.get_by_name('thisdoesnotexist')
        self.assertEqual(tag.tag_name, 'thisdoesnotexist')
    
    def test_get_public(self):
        tags = Tag.get_public()
        self.assertEqual(len(tags), 3)
    
    def test_get_by_user(self):
        tags = Tag.get_by_user(2)
        self.assertEqual(len(tags), 2)
    
    def test_get_public_by_user(self):
        tags = Tag.get_public_by_user(2)
        self.assertEqual(len(tags), 1)
    
    def test_get_cloud_by_user(self):
        tags = Tag.get_cloud_by_user(1);
        self.assertEqual(len(tags), 3)
        for t in tags:
            if t.tag_name == 'test1':
                self.assertEqual(t.link_count, 3)
            elif t.tag_name == 'blah':
                self.assertEqual(t.link_count, 2)
            elif t.tag_name == 'test2':
                self.assertEqual(t.link_count, 1)
            else:
                self.assertTrue(False, 'Got unexpected tags')
        
    
    
    
    