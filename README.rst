aldryn-sites
============

.. image:: https://travis-ci.org/aldryn/aldryn-sites.svg?branch=develop
    :target: https://travis-ci.org/aldryn/aldryn-sites

.. image:: https://img.shields.io/coveralls/aldryn/aldryn-sites.svg
  :target: https://coveralls.io/r/aldryn/aldryn-sites

Extensions to django.contrib.sites.

Features
--------

* **Domain redirects**: handles smart redirecting to a main domain from alias domains.
  Taking http/https into consideration.

* **Site auto-population**: automatically populates the Domain name in ``django.contrib.sites.Site.domain`` based
  on the ``ALDRYN_SITES_DOMAINS`` setting.


Installation
------------


* add ``aldryn_sites`` to ``INSTALLED_APPS``.

* add ``aldryn_sites.middleware.SiteMiddleware`` to ``MIDDLEWARE_CLASSES``
  (place it **before** ``djangosecure.middleware.SecurityMiddleware`` if redirects should be smart about alias domains
  possibly not having a valid certificate of their own. The middleware will pick up on ``SECURE_SSL_REDIRECT`` from
  ``django-secure``.)
  
configure ``ALDRYN_SITES_DOMAINS``::

    ALDRYN_SITES_DOMAINS = {
        1: {  # matches SITE_ID
            'domain': 'www.example.com',  # main domain that all the aliases will redirect to.
                                          # Auto populates ``django.contrib.sites.Site.domain``
            'aliases': [                  # these domains will be accessible like the main domain (no redirect).
                'an.other.domain.com',
            ],
            'redirects': [                # these domains will be redirected to the main domain.
                'example.com',            # add ``'*'`` to redirect all non-main domains to the main one.
                'example.ch',
                'www.example.ch',
            ],
        }
    }


Further Settings
----------------

set ``ALDRYN_SITES_SET_DOMAIN_NAME`` to ``False`` if you don't want ``django.contrib.sites.Site.domain`` to be
auto-populated (default: ``True``).


TODOS
-----

* validate settings
* test settings validators
* log warning if there are Sites in the database that are not in the settings
* pretty display of how redirects will work (in admin and as a simple util)
* regex support for aliases
* form to test redirect logic
