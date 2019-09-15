#i pylint: disable=invalid-name, wrong-import-position
import sys

from os.path import abspath, dirname
from unittest import TestCase

try:
    import unittest.mock as mock
except Exception:
    import mock

from mock import Mock

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import lnto
import lnto.views

class ViewTest(TestCase):

    render_templates = False

    def setUp(self):
        lnto.app.config['TESTING'] = True
        lnto.app.testing = True
        #lnto.app.login_manager.init_app(lnto.app)
        self.client = lnto.app.test_client()


    def test_new_user_when_registration_disabled_returns_403(self):
        lnto.app.config['ALLOW_REGISTRATION'] = False

        response = self.client.get('/users/new')

        assert "403 Forbidden" in str(response.data)


    def test_new_user_when_username_empty_display_error(self):
        lnto.app.config['ALLOW_REGISTRATION'] = True

        post_data = dict(username='  ', password='asdf', confirm='asdf')
        response = self.client.post('/users/new', data=post_data)

        assert "You must give a username" in str(response.data)


    def test_new_user_when_password_empty_display_error(self):
        lnto.app.config['ALLOW_REGISTRATION'] = True

        post_data = dict(username='bob', password='  ', confirm='test')
        response = self.client.post('/users/new', data=post_data)

        assert "You must give a password" in str(response.data)
        assert "Passwords do not match" in str(response.data)


    @mock.patch('lnto.views.User.save')
    @mock.patch('lnto.views.User.set_password')
    def test_new_user_when_form_valid_creates_new_user(self, mock_set_password, mock_save):
        lnto.app.config['ALLOW_REGISTRATION'] = True

        post_data = dict(username='bob', password='test', confirm='test')
        self.client.post('/users/new', data=post_data)

        mock_save.assert_called()
        mock_set_password.assert_called_with('test')


    @mock.patch('lnto.views.User.get_logged_in')
    @mock.patch('flask_login.utils._get_user')
    def test_change_password_passwords_do_not_match(self, user, mock_user):
        mock_user.return_value = Mock()
        user.return_value = Mock()

        post_data = dict(new_password='test1', confirm='test2')
        response = self.client.post('/user/password/change', data=post_data)

        assert "Passwords do not match" in str(response.data)


    @mock.patch('lnto.views.User.get_logged_in')
    @mock.patch('flask_login.utils._get_user')
    def test_change_password_when_password_valid_user_is_saved(self, user, mock_user):
        lnto.app.config['WTF_CSRF_ENABLED'] = False
        mock_user_instance = Mock()
        mock_user.return_value = mock_user_instance
        user.return_value = mock_user_instance

        post_data = dict(new_password='testpassword', confirm='testpassword')
        self.client.post('/user/password/change', data=post_data)

        mock_user_instance.set_password.assert_called_with('testpassword')
        assert mock_user_instance.save.called

    @mock.patch('lnto.views.User.get_logged_in')
    @mock.patch('lnto.views.Link')
    @mock.patch('flask_login.utils._get_user')
    def test_add_link_when_form_valid_saves_link(self, user, mock_link, mock_logged_in):
        lnto.app.config['WTF_CSRF_ENABLED'] = False
        mock_user = Mock()
        mock_user.userid = 1
        user.return_value = mock_user
        mock_logged_in.return_value = mock_user
        mock_link_instance = Mock()
        mock_link_instance.already_exists.return_value = False
        mock_link.return_value = mock_link_instance

        post_data = dict(
            name=u'Example',
            shortname=u'',
            url=u'http://example.com/',
            description=u'',
            tags=u'foo,bar',
            is_public=u'1'
        )
        self.client.post('/link/add', data=post_data)

        mock_link.assert_called_with(dict(
            userid=1,
            name=u'Example',
            shortname=u'',
            url=u'http://example.com/',
            description=u'',
            tags=u'foo,bar',
            is_public=True,
            referer='/',
            redirect_to_target='0'
        ))
        mock_link_instance.set_tags.assert_called_with([u'foo', u'bar'])
        mock_link_instance.save.assert_called()


    @mock.patch('lnto.views.User.get_logged_in')
    @mock.patch('lnto.views.Link')
    @mock.patch('lnto.views.Tag.get_by_user')
    @mock.patch('flask_login.utils._get_user')
    def test_add_link_when_missing_name_and_link_shows_errors(
            self,
            user,
            mock_get_by_user,
            mock_link,
            mock_logged_in):
        lnto.app.config['WTF_CSRF_ENABLED'] = False
        mock_user = Mock()
        mock_user.userid = 1
        user.return_value = mock_user
        mock_logged_in.return_value = mock_user
        mock_get_by_user.return_value = []
        mock_link_instance = Mock()
        mock_link_instance.already_exists.return_value = False
        mock_link_instance.get_taglist.return_value = ['foo', 'bar']
        mock_link.return_value = mock_link_instance

        post_data = dict(
            userid=u'1',
            name=u'',
            shortname=u'',
            url=u'',
            description=u'Test',
            tags=u'foo,bar',
            is_public=u'1'
        )
        response = self.client.post('/link/add', data=post_data)

        assert "Title is required" in str(response.data)
        assert "URL is required" in str(response.data)


    @mock.patch('lnto.views.User.get_logged_in')
    @mock.patch('lnto.views.Link')
    @mock.patch('lnto.views.flash')
    @mock.patch('flask_login.utils._get_user')
    def test_add_link_when_link_exists_shows_message(
            self,
            user,
            mock_flash,
            mock_link,
            mock_logged_in):
        lnto.app.config['WTF_CSRF_ENABLED'] = False
        mock_user = Mock()
        mock_user.userid = 1
        user.return_value = mock_user
        mock_logged_in.return_value = mock_user
        mock_link_instance = Mock()
        mock_link_instance.already_exists.return_value = True
        mock_link.return_value = mock_link_instance

        post_data = dict(
            userid=u'1',
            name=u'',
            shortname=u'',
            url=u'',
            description=u'Test',
            tags=u'',
            is_public=u'1'
        )
        self.client.post('/link/add', data=post_data)

        mock_flash.assert_called_with(
            'This link already exists.  Try editing it instead.',
            'error'
        )
