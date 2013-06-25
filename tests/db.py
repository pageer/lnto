import lnto
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.tags import Tag

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
            'description': 'This is a test',
            'tags': ['test1', 'test2']
        },
        {
            'name': 'Foo2',
            'userid': 1,
            'url': 'http://www.example.com/test',
            'shortname': 'foo2',
            'description': 'This is a test again',
            'tags': ['test1', 'blah']
        },
        {
            'name': 'Foo3',
            'userid': 1,
            'url': 'http://www.example.com/test3',
            'description': 'This is a test again',
            'tags': ['test1', 'blah'],
            'is_public': False
        },
        {
            'name': 'User2Foo',
            'userid': 2,
            'url': 'http://www.example.com/test4',
            'description': 'This is a test again',
            'tags': ['test1'],
        },
        {
            'name': 'User2Foo2',
            'userid': 2,
            'url': 'http://www.example.com/test5',
            'description': 'This is a test again',
            'tags': ['privatetag'],
            'is_public': False
        }
    ]
    user_data = [
        {
            'username': 'testuser',
            'password': 'test1'
        },
        {
            'username': 'testuser2',
            'password': 'test2'
        }
    ]
    
    for user in user_data:
        u = User(user)
        u.set_password(user['password'])
        u.save()
    
    for link in link_data:
        l = Link(link)
        l.save()
