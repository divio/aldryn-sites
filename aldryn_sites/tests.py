# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from . import utils
from django.test import TestCase


class AldrynSitesTestCase(TestCase):
    def test_http_redirect_url(self):
        config = {
            'domain': 'www.default.com',
            'aliases': [
                'an.other.domain.com',
            ],
            'redirects': [
                'default.com',
                'default.io',
                'www.default.io',
            ]
        }
        expected_redirects = [
            ('http://www.default.com', None),
            ('http://www.default.com/something/', None),
            ('http://default.com/', 'http://www.default.com/'),
            ('http://default.com/something/', 'http://www.default.com/something/'),
            ('http://default.io', 'http://www.default.com'),
            ('http://www.default.io/', 'http://www.default.com/'),
            ('http://an.other.domain.com/', None),

            ('https://www.default.com', 'http://www.default.com'),
            ('https://www.default.com/something/', 'http://www.default.com/something/'),
            ('https://default.com/', 'http://www.default.com/'),
            ('https://default.com/something/', 'http://www.default.com/something/'),
            ('https://default.io', 'http://www.default.com'),
            ('https://www.default.io/', 'http://www.default.com/'),
            ('https://an.other.domain.com/', 'http://an.other.domain.com/'),
        ]
        for src, dst in expected_redirects:
            self.assertEqual(dst, utils.get_redirect_url(src, config=config, https=False))

    def test_https_redirect_url(self):
        config = {
            'domain': 'www.default.com',
            'aliases': [
                'an.other.domain.com',
            ],
            'redirects': [
                'default.com',
                'default.io',
                'www.default.io',
            ]
        }
        expected_redirects = [
            ('https://www.default.com', None),
            ('http://www.default.com', 'https://www.default.com'),

            ('https://www.default.com/something/', None),
            ('http://www.default.com/something/', 'https://www.default.com/something/'),

            ('https://default.com/', 'https://www.default.com/'),
            ('http://default.com/', 'https://www.default.com/'),

            ('https://default.com/something/', 'https://www.default.com/something/'),
            ('http://default.com/something/', 'https://www.default.com/something/'),

            ('https://default.io', 'https://www.default.com'),
            ('http://default.io', 'https://www.default.com'),

            ('https://www.default.io/', 'https://www.default.com/'),
            ('http://www.default.io/', 'https://www.default.com/'),

            ('https://an.other.domain.com/', None),
            ('http://an.other.domain.com/', 'https://an.other.domain.com/'),

        ]
        for src, dst in expected_redirects:
            self.assertEqual(dst, utils.get_redirect_url(src, config=config, https=True))
