import sys

from os.path import abspath, dirname
from flask import Flask
#from flask_testing import TestCase
from unittest import TestCase

try:
    import unittest.mock as mock
except:
    import mock

from mock import Mock

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import lnto
import lnto.views
from lnto.libs.users import User

class ViewTest(TestCase):

    render_templates = False

    def setUp(self):
        lnto.app.testing = True
        self.client = lnto.app.test_client()

    def test_new_user_when_registration_disabled_returns_403(self):
        lnto.app.config['ALLOW_REGISTRATION'] = False

        response = self.client.get('/users/new')

        assert "403 Forbidden" in response.data


    @mock.patch('lnto.views.User.get_logged_in')
    def test_change_password_passwords_do_not_match(self, mock_user):
        mock_user.return_value = Mock()

        post_data = dict(new_password='test1', confirm='test2')
        response = self.client.post('/user/password/change', data=post_data)

        assert "Passwords do not match" in response.data


    @mock.patch('lnto.views.User.get_logged_in')
    def test_change_password_when_password_valid_user_is_saved(self, mock_user):
        lnto.app.config['WTF_CSRF_ENABLED'] = False
        mock_user_instance = Mock()
        mock_user.return_value = mock_user_instance

        post_data = dict(new_password='testpassword', confirm='testpassword')
        self.client.post('/user/password/change', data=post_data)

        mock_user_instance.set_password.assert_called_with('testpassword')
        assert mock_user_instance.save.called
