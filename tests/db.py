import lnto
from lnto.libs.links import Link
from lnto.libs.links import LinkHit
from lnto.libs.users import User
from lnto.libs.tags import Tag

from datetime import datetime

def init_test_db():
    
    lnto.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'
    lnto.appdb.init_app(lnto.app)
    lnto.appdb.create_all()
    create_test_data()

def delete_test_db():
    lnto.appdb.drop_all()

def create_test_data():
    link_data = [
        {
            'name': 'Foo',
            'userid': 1,
            'url': 'http://www.example.com/',
            'shortname': 'foo',
            'added': datetime(2013, 2, 1, 12, 13, 14),
            'description': 'This is a test',
            'tags': 'test1, test2'
        },
        {
            'name': 'Foo2',
            'userid': 1,
            'url': 'http://www.example.com/test',
            'shortname': 'foo2',
            'added': datetime(2013, 2, 2, 12, 13, 14),
            'description': 'This is a test again',
            'tags': 'test1, blah'
        },
        {
            'name': 'Foo3',
            'userid': 1,
            'url': 'http://www.example.com/test3',
            'description': 'This is a test again',
            'added': datetime(2013, 2, 3, 12, 13, 14),
            'tags': 'test1, blah',
            'is_public': False
        },
        {
            'name': 'User2Foo',
            'userid': 2,
            'url': 'http://www.example.com/test4',
            'description': 'This is a test again',
            'added': datetime(2013, 2, 3, 15, 16, 17),
            'tags': 'test1',
        },
        {
            'name': 'User2Foo2',
            'userid': 2,
            'url': 'http://www.example.com/test5',
            'description': 'This is a test again',
            'added': datetime(2013, 1, 2, 12, 13, 14),
            'tags': 'privatetag',
            'is_public': False
        },
        {
            'name': 'User3Foo3',
            'userid': 3,
            'url': 'http://www.example.com/test6',
            'description': 'This is a test again',
            'added': datetime(2013, 1, 2, 12, 13, 14),
            'tags': '',
            'is_public': False
        },
        {
            'name': 'User4Foo4',
            'userid': 4,
            'url': 'http://www.example.com/test7',
            'description': 'This is a test again',
            'added': datetime(2013, 1, 2, 12, 13, 14),
            'tags': '',
            'is_public': True
        },
        {
            'name': 'User3Foo3',
            'userid': 3,
            'url': 'http://www.example.com/test6',
            'description': 'This is a test again',
            'added': datetime(2013, 1, 2, 12, 13, 14),
            'tags': 'userid3',
            'is_public': False
        },
        {
            'name': 'User4Foo4',
            'userid': 4,
            'url': 'http://www.example.com/test7',
            'description': 'This is a test again',
            'added': datetime(2013, 1, 2, 12, 13, 14),
            'tags': 'userid4',
            'is_public': True
        },
    ]
    user_data = [
        {
            'username': 'testuser',
            'password': 'test1'
        },
        {
            'username': 'testuser2',
            'password': 'test2'
        },
        {
            'username': 'testuser3',
            'password': 'test3'
        },
        {
            'username': 'testuser4',
            'password': 'test4'
        }
    ]
    hit_data = [
        {
            'linkid': 1,
            'userid': 1,
            'ts': datetime(2013, 1, 2, 12, 13, 14)
        },
        {
            'linkid': 1,
            'userid': 2,
            'ts': datetime(2013, 3, 4, 17, 18, 19)
        },
        {
            'linkid': 2,
            'userid': 2,
            'ts': datetime(2013, 3, 4, 17, 18, 10)
        },
        {
            'linkid': 4,
            'userid': 1,
            'ts': datetime(2013, 2, 3, 16, 17, 18)
        }
    ]
    
    for user in user_data:
        u = User(user)
        u.set_password(user['password'])
        u.save()
    
    for link in link_data:
        l = Link(link)
        l.save()
    
    for hit in hit_data:
        h = LinkHit(hit)
        lnto.appdb.session.add(h)
        lnto.appdb.session.commit()
    
