# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from . import utils
import re
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
            self.assertEqual(dst, utils.get_redirect_url(src, config=config, https=False),
                             msg='expected {} -> {}. got {}'.format(
                                 src, dst, utils.get_redirect_url(
                                     src, config=config, https=True)))

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
            self.assertEqual(dst, utils.get_redirect_url(src, config=config, https=True),
                             msg='expected {} -> {}. got {}'.format(
                                 src, dst, utils.get_redirect_url(
                                     src, config=config, https=True)))

    def test_https_pattern_priority_matches(self):
        config = {
            'domain': 'www.default.com',
            'aliases': [
                'an.other.domain.com',
                'exact.default.io',
                r'^[a-z0-9-]+\.default\.com$',
                r'^[a-z0-9-]+\.default\.me$',
            ],
            'redirects': [
                'default.com',
                'default.io',
                'exact.default.me',
                'www.default.io',
                r'^[a-z0-9-]+\.default\.com$',
                re.compile(r'^[a-z0-9-]+\.default\.io$'),  # it's possible to put a pre-compiled regex here
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

            # redirect pattern should win over alias pattern
            ('https://pattern.default.com/', 'https://www.default.com/'),

            # exact alias should win over pattern redirect
            ('https://www.default.com', None),
            ('https://exact.default.io', None),

            # exact redirect should win over alias pattern
            ('https://exact.default.me', 'https://www.default.com'),
        ]
        for src, dst in expected_redirects:
            self.assertEqual(dst, utils.get_redirect_url(src, config=config, https=True),
                             msg='expected {} -> {}. got {}'.format(
                                 src, dst, utils.get_redirect_url(
                                     src, config=config, https=True)))

    def test_auto_configure_allowed_hosts(self):
        from django.conf import settings
        for domain in ['www.example.com', 'example.com', 'an.other.domain.com']:
            self.assertTrue(domain in settings.ALLOWED_HOSTS, '{} not in ALLOWED_HOSTS'.format(domain))

    def test_auto_configure_site_domain(self):
        from django.contrib.sites.models import Site
        Site.objects.all().delete()
        Site.objects.create(name='Acme Ltd', domain='acme.com')
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertTrue(s.name == 'Acme Ltd', 'site name has changed')
        self.assertTrue(s.domain == 'www.example.com', 'site domain was not set')

    def test_auto_configure_site_domain_and_name_if_same(self):
        from django.contrib.sites.models import Site
        Site.objects.all().delete()
        Site.objects.create(name='acme.com', domain='acme.com')
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertTrue(s.name == 'www.example.com', 'site name was not set')
        self.assertTrue(s.domain == 'www.example.com', 'site domain was not set')

    def test_auto_configure_adds_new_sites(self):
        from django.contrib.sites.models import Site
        Site.objects.all().delete()
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertTrue(s.name == 'www.example.com', 'site name was not set')
        self.assertTrue(s.domain == 'www.example.com', 'site domain was not set')

    def test_auto_configure_adds_multiple_new_sites_with_one_existing(self):
        from django.contrib.sites.models import Site
        with self.settings(ALDRYN_SITES_DOMAINS={
                1: {'domain': 'www.example.com'},
                2: {'domain': 'www.other.com'},
                }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=1)
            self.assertTrue(s.name == 'www.example.com', 'site name was not set')
            self.assertTrue(s.domain == 'www.example.com', 'site domain was not set')
            s = Site.objects.get(id=2)
            self.assertTrue(s.name == 'www.other.com', 'site name was not set')
            self.assertTrue(s.domain == 'www.other.com', 'site domain was not set')
