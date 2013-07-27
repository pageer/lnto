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
    
    def test_add_tag_and_get(self):
        self.link.add_tag('test5')
        self.assertTrue('test5' in self.link.get_taglist())
    
    def test_add_tag_duplicate(self):
        taglist = self.link.get_taglist()
        self.link.add_tag('test1')
        self.assertTrue(taglist == self.link.get_taglist())
    
    def test_get_by_id_exists(self):
        result = Link.get_by_id(1)
        self.assertTrue(result.__class__ is Link)
    
    def test_get_by_id_nonexistent(self):
        result = Link.get_by_id(123)
        self.assertEqual(result, None)
    
    def test_get_by_id_array_all_exist(self):
        result = Link.get_by_id([1, 2])
        self.assertEqual(len(result), 2)
    
    def test_get_by_id_array_one_exists(self):
        result = Link.get_by_id([1, 123])
        self.assertEqual(len(result), 1)
    
    def test_get_by_id_array_none_exist(self):
        result = Link.get_by_id([234, 123])
        self.assertEqual(len(result), 0)
    
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
    
    def test_get_by_most_hits(self):
        result = Link.get_by_most_hits()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].linkid, 1)
    
    def test_get_by_most_hits_with_owner(self):
        result = Link.get_by_most_hits(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].linkid, 1)
        self.assertEqual(result[1].linkid, 2)
    
    def test_get_by_most_hits_with_limit(self):
        result = Link.get_by_most_hits(1, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].linkid, 1)
    
    def test_get_by_most_recent_hit(self):
        result = Link.get_by_most_hits()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].linkid, 1)
    
    def test_get_by_most_recent_hit_with_owner(self):
        result = Link.get_by_most_hits(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].linkid, 1)
        self.assertEqual(result[1].linkid, 2)
    
    def test_get_by_most_recent_hit_with_limit(self):
        result = Link.get_by_most_hits(1, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].linkid, 1)
    
    def test_get_by_most_recent(self):
        result = Link.get_by_most_recent()
        self.assertEqual(len(result), 9)
        self.assertEqual(result[0].linkid, 4)
    
    def test_get_by_most_recent_with_owner(self):
        result = Link.get_by_most_recent(1)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].linkid, 3)
    
    def test_get_by_most_recent_with_limit(self):
        result = Link.get_by_most_recent(1, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].linkid, 3)
    
    def test_get_untagged(self):
        result = Link.get_untagged()
        self.assertEqual(len(result), 2)
    
    def test_get_untagged_with_owner(self):
        result = Link.get_untagged(3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].linkid, 6)
        
    def test_get_public_untagged(self):
        result = Link.get_public_untagged()
        for r in result:
            print str(r.linkid) + ' ' + str(r.is_public)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].linkid, 7)
    
    def test_get_public_untagged_with_owner(self):
        result = Link.get_public_untagged(4)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].linkid, 7)
        result = Link.get_public_untagged(3)
        self.assertEqual(len(result), 0)
    
    def test_create_from_webpage(self):
        url = 'http://www.example.com'
        html = """
        <html>
        <head>
            <title>This is a test</title>
        </head>
        <body>Test</body>
        </html>
        """
        link = Link.create_from_webpage(url, html)
        self.assertEqual(link.url, url)
        self.assertEqual(link.name, 'This is a test')
    
    def test_create_from_webpage_with_description(self):
        url = 'http://www.example.com'
        html = """
        <html>
        <head>
            <title>This is a test</title>
            <meta name="description" content="Describe this page" />
        </head>
        <body>Test</body>
        </html>
        """
        link = Link.create_from_webpage(url, html)
        self.assertEqual(link.url, url)
        self.assertEqual(link.name, 'This is a test')
        self.assertEqual(link.description, "Describe this page")
    
        