0.5.4 (2016-08-06)
------------------

* do not redirect from https to http if `SECURE_SSL_REDIRECT` is not
  explicitly set to `False`


0.5.2 (2015-12-31)
------------------

* fix tests to support Django 1.7, 1.8, 1.9
* middleware: use 302 (temporary redirect), not 301 (permanent)


0.5.1 (2015-10-29)
------------------

* add Django 1.5 support


0.5 (2015-01-22)
----------------

* auto configuration of Site.name if it matches Site.domain


0.4 (2014-11-27)
----------------

* auto configuration of ALLOWED_HOSTS
* regex domain matching support


0.3 (2014-11-25)
----------------

* adds distinction between aliases and redirects
  (Backwards incompatible change! 'aliases' is now called 'redirects')


0.2 (2014-11-18)
----------------

Initial Release
