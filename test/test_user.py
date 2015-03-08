#!/usr/bin/env python

from test_base import TestBase
import logging


class UserTest(TestBase):

    def test_jws(self):

        user = self.auth_api_call('post', '/users', {
            'username': self.USERNAME,
            'hostname': self.HOSTNAME
        }).json
        assert user['id'] == self.USERNAME
        assert len(user['todo_lists']) == 1

        user = self.auth_api_call('get', '/users/' + self.USERNAME, {
            'username': self.USERNAME,
            'hostname': self.HOSTNAME
        }).json
        assert user['id'] == self.USERNAME
        assert len(user['todo_lists']) == 1

    # TODO def test_mocks(self):
