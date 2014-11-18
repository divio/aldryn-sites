# -*- coding: utf-8 -*-
HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'aldryn_sites',
    ],
    'MIDDLEWARE_CLASSES': [
        'aldryn_sites.middleware.SiteMiddleware',
    ],
    'ALDRYN_SITES_DOMAINS': {
        1: {
            'domain': 'www.example.com',
            'aliases': [
                'example.com',
            ]
        }
    }
}
