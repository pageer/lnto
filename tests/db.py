from datetime import datetime
import os

import sqlalchemy

import lnto
from lnto.libs.links import Link
from lnto.libs.links import LinkHit
from lnto.libs.users import User

_test_ctx = None
_test_db_path = os.path.join(os.path.dirname(lnto.__file__), 'tmp.db')

def init_test_db():

    uri = 'sqlite:///' + _test_db_path.replace('\\', '/')
    lnto.app.config['SQLALCHEMY_DATABASE_URI'] = uri
    # Flask-SQLAlchemy 3.x creates the engine once at init_app time and
    # refuses a second init_app, so install a fresh engine for the test
    # database directly. Also push an app context, which is required for
    # create_all and any session use during the test.
    with lnto.app.app_context():
        lnto.appdb.engines.pop(None, None)
        lnto.appdb.engines[None] = sqlalchemy.create_engine(uri)
    global _test_ctx
    _test_ctx = lnto.app.app_context()
    _test_ctx.push()
    lnto.appdb.create_all()
    create_test_data()

def delete_test_db():
    lnto.appdb.drop_all()
    _test_ctx.pop()

_test_ctx = None

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
        user_obj = User(user)
        user_obj.set_password(user['password'])
        user_obj.save()

    for link in link_data:
        link_obj = Link(link)
        link_obj.save()

    for hit in hit_data:
        hit_obj = LinkHit(hit)
        lnto.appdb.session.add(hit_obj)
        lnto.appdb.session.commit()
