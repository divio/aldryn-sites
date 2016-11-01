# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import re

from unittest import skipIf

import yurl

from django import VERSION as DJANGO_VERSION
from django.test import TestCase, RequestFactory
from django.contrib.sites.models import Site

from . import utils, middleware


class RedirectOnlyTestingSiteMiddleware(middleware.SiteMiddleware):
    def __init__(self, site_id, domains, secure_redirect):
        self.site_id = site_id
        self.domains = domains
        self.secure_redirect = secure_redirect


class AldrynSitesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def request_from_url(self, url):
        url = yurl.URL(url)
        secure = (url.scheme == 'https')
        # Django < 1.7 does not have the `secure` parameter for the request
        # factory methods. Manually set the required kwargs here instead.
        kwargs = {
            'SERVER_NAME': url.host,
            'SERVER_PORT': str('443') if secure else str('80'),
            'wsgi.url_scheme': str('https') if secure else str('http'),
        }
        return self.factory.get(
            url.full_path,
            **kwargs
        )

    def assertUrlEquals(self, src, expected, got):
        return self.assertEquals(
            expected,
            got,
            msg='expected {} -> {}. got {}'.format(src, expected, got),
        )

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
            ('https://www.default.com/', 'http://www.default.com/'),
            ('http://www.default.com/', None),

            ('https://www.default.com/something/', 'http://www.default.com/something/'),
            ('http://www.default.com/something/', None),

            ('https://default.com/', 'http://www.default.com/'),
            ('http://default.com/', 'http://www.default.com/'),

            ('https://default.com/something/', 'http://www.default.com/something/'),
            ('http://default.com/something/', 'http://www.default.com/something/'),

            ('https://default.io/', 'http://www.default.com/'),
            ('http://default.io/', 'http://www.default.com/'),

            ('https://www.default.io/', 'http://www.default.com/'),
            ('http://www.default.io/', 'http://www.default.com/'),

            ('https://an.other.domain.com/', 'http://an.other.domain.com/'),
            ('http://an.other.domain.com/', None),
        ]
        with self.settings(
            ALDRYN_SITES_DOMAINS={1: config},
            SECURE_SSL_REDIRECT=False,
        ):
            site_middleware = middleware.SiteMiddleware()

        for src, expected in expected_redirects:
            redirected = utils.get_redirect_url(src, config=config, https=False)
            self.assertUrlEquals(src, expected, redirected)

            response = site_middleware.process_request(self.request_from_url(src))
            if expected is None:
                self.assertIsNone(response)
            else:
                self.assertUrlEquals(src, expected, response['Location'])

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
            ('https://www.default.com/', None),
            ('http://www.default.com/', 'https://www.default.com/'),

            ('https://www.default.com/something/', None),
            ('http://www.default.com/something/', 'https://www.default.com/something/'),

            ('https://default.com/', 'https://www.default.com/'),
            ('http://default.com/', 'https://www.default.com/'),

            ('https://default.com/something/', 'https://www.default.com/something/'),
            ('http://default.com/something/', 'https://www.default.com/something/'),

            ('https://default.io/', 'https://www.default.com/'),
            ('http://default.io/', 'https://www.default.com/'),

            ('https://www.default.io/', 'https://www.default.com/'),
            ('http://www.default.io/', 'https://www.default.com/'),

            ('https://an.other.domain.com/', None),
            ('http://an.other.domain.com/', 'https://an.other.domain.com/'),
        ]

        with self.settings(
            ALDRYN_SITES_DOMAINS={1: config},
            SECURE_SSL_REDIRECT=True,
        ):
            site_middleware = middleware.SiteMiddleware()

        for src, expected in expected_redirects:
            redirected = utils.get_redirect_url(src, config=config, https=True)
            self.assertUrlEquals(src, expected, redirected)

            response = site_middleware.process_request(self.request_from_url(src))
            if expected is None:
                self.assertIsNone(response)
            else:
                self.assertUrlEquals(src, expected, response['Location'])

    def test_no_scheme_redirect_url(self):
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
            ('http://www.default.com', None),

            ('https://www.default.com/something/', None),
            ('http://www.default.com/something/', None),

            ('https://default.com/', 'https://www.default.com/'),
            ('http://default.com/', 'http://www.default.com/'),

            ('https://default.com/something/', 'https://www.default.com/something/'),
            ('http://default.com/something/', 'http://www.default.com/something/'),

            ('https://default.io/', 'https://www.default.com/'),
            ('http://default.io/', 'http://www.default.com/'),

            ('https://www.default.io/', 'https://www.default.com/'),
            ('http://www.default.io/', 'http://www.default.com/'),

            ('https://an.other.domain.com/', None),
            ('http://an.other.domain.com/', None),

        ]
        with self.settings(
            ALDRYN_SITES_DOMAINS={1: config},
            SECURE_SSL_REDIRECT=None,
        ):
            site_middleware = middleware.SiteMiddleware()

        for src, expected in expected_redirects:
            redirected = utils.get_redirect_url(src, config=config, https=None)
            self.assertUrlEquals(src, expected, redirected)

            response = site_middleware.process_request(self.request_from_url(src))
            if expected is None:
                self.assertIsNone(response)
            else:
                self.assertUrlEquals(src, expected, response['Location'])

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
            ('https://www.default.com/', None),
            ('http://www.default.com/', 'https://www.default.com/'),

            ('https://www.default.com/something/', None),
            ('http://www.default.com/something/', 'https://www.default.com/something/'),

            ('https://default.com/', 'https://www.default.com/'),
            ('http://default.com/', 'https://www.default.com/'),

            ('https://default.com/something/', 'https://www.default.com/something/'),
            ('http://default.com/something/', 'https://www.default.com/something/'),

            ('https://default.io/', 'https://www.default.com/'),
            ('http://default.io/', 'https://www.default.com/'),

            ('https://www.default.io/', 'https://www.default.com/'),
            ('http://www.default.io/', 'https://www.default.com/'),

            ('https://an.other.domain.com/', None),
            ('http://an.other.domain.com/', 'https://an.other.domain.com/'),

            # redirect pattern should win over alias pattern
            ('https://pattern.default.com/', 'https://www.default.com/'),

            # exact alias should win over pattern redirect
            ('https://www.default.com/', None),
            ('https://exact.default.io/', None),

            # exact redirect should win over alias pattern
            ('https://exact.default.me/', 'https://www.default.com/'),
        ]
        for src, expected in expected_redirects:
            redirected = utils.get_redirect_url(src, config=config, https=True)
            self.assertEqual(
                expected,
                redirected,
                msg='expected {} -> {}. got {}'.format(src, expected, redirected),
            )

    @skipIf(DJANGO_VERSION >= (1, 7),
            "Does not work inside tests on this version")
    def test_auto_configure_allowed_hosts(self):
        from django.conf import settings
        for domain in ['www.project.com', 'project.com', 'an.other.domain.com']:
            self.assertIn(domain, settings.ALLOWED_HOSTS)

    def test_auto_configure_adds_new_sites(self):
        Site.objects.all().delete()
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertEquals(s.name, 'My Project')
        self.assertEquals(s.domain, 'www.project.com')

    def test_auto_configure_adds_multiple_new_sites_with_one_existing(self):
        Site.objects.all().delete()
        with self.settings(ALDRYN_SITES_DOMAINS={
            1: {'name': 'Site 1', 'domain': 'site1.com'},
            2: {'name': 'Site 2', 'domain': 'site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=1)
            self.assertEquals(s.name, 'Site 1')
            self.assertEquals(s.domain, 'site1.com')
            s = Site.objects.get(id=2)
            self.assertEquals(s.name, 'Site 2')
            self.assertEquals(s.domain, 'site2.com')

    def test_sitename(self):
        Site.objects.all().delete()
        with self.settings(ALDRYN_SITES_DOMAINS={
            1: {'domain': 'site1.com'},
            2: {'name': 'Site 2', 'domain': 'site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=1)
            self.assertEquals(s.name, 'site1.com')
            self.assertEquals(s.domain, 'site1.com')
            s = Site.objects.get(id=2)
            self.assertEquals(s.name, 'Site 2')
            self.assertEquals(s.domain, 'site2.com')

    def test_domain_changed_matching_name(self):
        Site.objects.all().delete()
        site_1 = Site.objects.create(name='site1.com', domain='site1.com')
        site_2 = Site.objects.create(name='site2.com', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'domain': 'other-site1.com'},
            site_2.pk: {'name': 'Other Site 2', 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'site1.com')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'site2.com')
            self.assertEquals(s.domain, 'other-site2.com')

    def test_domain_changed_different_name(self):
        Site.objects.all().delete()
        site_1 = Site.objects.create(name='Site 1', domain='site1.com')
        site_2 = Site.objects.create(name='Site 2', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'domain': 'other-site1.com'},
            site_2.pk: {'name': 'Other Site 2', 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'Site 1')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'Site 2')
            self.assertEquals(s.domain, 'other-site2.com')
