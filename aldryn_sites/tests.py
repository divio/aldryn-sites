# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import re
from unittest import skipIf
from django import VERSION as DJANGO_VERSION
from django.test import TestCase

from . import utils


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

    @skipIf(DJANGO_VERSION >= (1, 7),
            "Does not work inside tests on this version")
    def test_auto_configure_allowed_hosts(self):
        from django.conf import settings
        for domain in ['www.project.com', 'project.com', 'an.other.domain.com']:
            self.assertIn(domain, settings.ALLOWED_HOSTS)

    def test_auto_configure_site_domain_and_name_if_same(self):
        from django.conf import settings
        from django.contrib.sites.models import Site
        Site.objects.all().delete()
        pk = settings.ALDRYN_SITES_DOMAINS.keys()[0]
        Site.objects.create(pk=pk, name='acme.com', domain='acme.com')
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertEquals(s.name, 'My Project')
        self.assertEquals(s.domain, 'www.project.com')

    def test_auto_configure_adds_new_sites(self):
        from django.contrib.sites.models import Site
        Site.objects.all().delete()
        utils.set_site_names(force=True)
        s = Site.objects.get()
        self.assertEquals(s.name, 'My Project')
        self.assertEquals(s.domain, 'www.project.com')

    def test_auto_configure_adds_multiple_new_sites_with_one_existing(self):
        from django.contrib.sites.models import Site
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
        from django.contrib.sites.models import Site
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

    def test_sitename_same_as_domain(self):
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='site1.com', domain='site1.com')
        site_2 = Site.objects.create(name='site2.com', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'domain': 'other-site1.com'},
            site_2.pk: {'name': 'Other Site 2', 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'other-site1.com')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'Other Site 2')
            self.assertEquals(s.domain, 'other-site2.com')

    def test_sitename_different_than_domain(self):
        from django.contrib.sites.models import Site

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
            self.assertEquals(s.name, 'Other Site 2')
            self.assertEquals(s.domain, 'other-site2.com')

    def test_sitename_is_example_com(self):
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='example.com', domain='example1.com')
        site_2 = Site.objects.create(name='example.com', domain='example2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'domain': 'other-site1.com'},
            site_2.pk: {'name': 'Other Site 2', 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)
            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'other-site1.com')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'Other Site 2')
            self.assertEquals(s.domain, 'other-site2.com')

    def test_domain_unchanged_new_sitename_empty_domain_different(self):
        """
        New Domain == site.domain
        New site.name: missing, '' or None
        Existing site.name != site.domain
        """
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='Site 1', domain='site1.com')
        site_2 = Site.objects.create(name='Site 2', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'name': '', 'domain': 'site1.com'},
            site_2.pk: {'name': None, 'domain': 'site2.com'},
        }):
            utils.set_site_names(force=True)

            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'Site 1')
            self.assertEquals(s.domain, 'site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'Site 2')
            self.assertEquals(s.domain, 'site2.com')

    def test_domain_unchanged_new_sitename_empty_domain_matches(self):
        """
        New Domain == site.domain
        New site.name: missing, '' or None
        site.name == site.domain
        """
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='site1.com', domain='site1.com')
        site_2 = Site.objects.create(name='site2.com', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'name': '', 'domain': 'site1.com'},
            site_2.pk: {'name': None, 'domain': 'site2.com'},
        }):
            utils.set_site_names(force=True)

            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'site1.com')
            self.assertEquals(s.domain, 'site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'site2.com')
            self.assertEquals(s.domain, 'site2.com')

    def test_domain_changes_new_sitename_empty_domain_different(self):
        """
        New Domain != site.domain
        New site.name: missing, '' or None
        site.name != site.domain
        """
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='Site 1', domain='site1.com')
        site_2 = Site.objects.create(name='Site 2', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'name': '', 'domain': 'other-site1.com'},
            site_2.pk: {'name': None, 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)

            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'Site 1')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'Site 2')
            self.assertEquals(s.domain, 'other-site2.com')

    def test_domain_changes_new_sitename_empty_domain_matches(self):
        """
        New Domain != site.domain
        New site.name: missing, '' or None
        site.name == site.domain
        """
        from django.contrib.sites.models import Site

        site_1 = Site.objects.create(name='site1.com', domain='site1.com')
        site_2 = Site.objects.create(name='site2.com', domain='site2.com')

        with self.settings(ALDRYN_SITES_DOMAINS={
            site_1.pk: {'name': '', 'domain': 'other-site1.com'},
            site_2.pk: {'name': None, 'domain': 'other-site2.com'},
        }):
            utils.set_site_names(force=True)

            s = Site.objects.get(id=site_1.pk)
            self.assertEquals(s.name, 'other-site1.com')
            self.assertEquals(s.domain, 'other-site1.com')

            s = Site.objects.get(id=site_2.pk)
            self.assertEquals(s.name, 'other-site2.com')
            self.assertEquals(s.domain, 'other-site2.com')
