import unittest
import lnto
import tests.db
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.tags import Tag

class TestLinks(unittest.TestCase):
    
    def setUp(self):
        tests.db.init_test_db()
        self.link = Link()
        self.link.userid = 1
        self.link.name = 'Test link'
        self.link.url = 'http://www.example.com/'
        self.link.tags = [Tag('test1'), Tag('test2')]
    
    def tearDown(self):
        tests.db.delete_test_db()
    
    def make_user(self, userid):
        usr = User()
        usr.userid = userid
        return usr
    
    def test_is_owner_same_user(self):
        u = self.make_user(1)
        self.assertTrue(self.link.is_owner(u))
    
    def test_is_owner_different_user(self):
        u = self.make_user(2)
        self.assertFalse(self.link.is_owner(u))
    
    def test_is_owner_empty_user(self):
        u = None
        self.assertFalse(self.link.is_owner(u))
    
    def test_get_taglist_has_tags(self):
        self.assertEqual(len(self.link.tags), 2)
        self.assertTrue('test1' in self.link.get_taglist())
        self.assertTrue('test2' in self.link.get_taglist())
        
    def test_get_taglist_no_tags(self):
        self.link.tags = []
        self.assertEqual(self.link.get_taglist(), [])
    
    def test_set_tags_and_get(self):
        self.link.set_tags(['test3', 'test4'])
        self.assertEqual(len(self.link.tags), 2)
        self.assertTrue('test3' in self.link.get_taglist())
        self.assertTrue('test4' in self.link.get_taglist())
    
    def test_get_by_id_exists(self):
        result = Link.get_by_id(1)
        self.assertTrue(result.__class__ is Link)
    
    def test_get_by_id_nonexistent(self):
        result = Link.get_by_id(123)
        self.assertEqual(result, None)
    
    def test_get_by_user_exists(self):
        result = Link.get_by_user(1)
        self.assertEqual(len(result), 3)
    
    def test_get_by_user_nonexistent(self):
        result = Link.get_by_user(123)
        self.assertEqual(len(result), 0)
    
    def test_get_public_by_user_exists(self):
        result = Link.get_public_by_user(1)
        self.assertEqual(len(result), 2)
    
    def test_get_public_by_user_nonexistent(self):
        result = Link.get_public_by_user(123)
        self.assertEqual(len(result), 0)
    
    def test_get_by_shortname_exists(self):
        result = Link.get_by_shortname('foo')
        self.assertEqual(result.__class__, Link)
    
    def test_get_by_shortname_nonexistent(self):
        result = Link.get_by_shortname('this does not exist')
        self.assertEqual(result, None)
    
    def test_get_by_tag_exists_nouser(self):
        result = Link.get_by_tag('test1')
        self.assertEqual(len(result), 4)
    
    def test_get_by_tag_exists_hasuser(self):
        result = Link.get_by_tag('test1', 1)
        self.assertEqual(len(result), 3)
    
    def test_get_by_tag_nonexistent_nouser(self):
        result = Link.get_by_tag('this does not exist')
        self.assertEqual(len(result), 0)
    
    def test_get_by_tag_nonexistent_hasuser(self):
        result = Link.get_by_tag('this does not exist', 1)
        self.assertEqual(len(result), 0)
    
    def test_get_public_by_tag_exists_nouser(self):
        result = Link.get_public_by_tag('test1')
        self.assertEqual(len(result), 3)
    
    def test_get_public_by_tag_exists_hasuser(self):
        result = Link.get_public_by_tag('test1', 1)
        self.assertEqual(len(result), 2)
    
    def test_get_public_by_tag_nonexistent_nouser(self):
        result = Link.get_public_by_tag('this does not exist')
        self.assertEqual(len(result), 0)
    
    def test_get_public_by_tag_nonexistent_hasuser(self):
        result = Link.get_public_by_tag('this does not exist', 1)
        self.assertEqual(len(result), 0)
    