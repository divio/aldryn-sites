# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion
from django import get_version


django_version = LooseVersion(get_version())

HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'aldryn_sites',
    ],
    'MIDDLEWARE_CLASSES': [
        'aldryn_sites.middleware.SiteMiddleware',
    ],
    'ALDRYN_SITES_DOMAINS': {
        1: {
            'name': 'My Project',
            'domain': 'www.project.com',
            'aliases': [
                'an.other.domain.com'
            ],
            'redirects': [
                'project.com',
            ],
        }
    },
}


def run():
    from djangocms_helper import runner
    runner.run('aldryn_sites')


if __name__ == "__main__":
    run()
