# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from appconf import AppConf


class AldrynSitesConf(AppConf):
    DOMAINS = {}
    SET_DOMAIN_NAME = True

    # TODO: validate settings
