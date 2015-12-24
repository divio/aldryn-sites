# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf import settings  # NOQA required so settings get initialised
from appconf import AppConf
from . import utils


class AldrynSitesConf(AppConf):
    DOMAINS = {}
    SET_DOMAIN_NAME = True
    AUTO_CONFIGURE_ALLOWED_HOSTS = True

    # TODO: validate settings

    def configure(self):
        if self.configured_data['AUTO_CONFIGURE_ALLOWED_HOSTS'] and self.configured_data['DOMAINS']:
            s = self._meta.holder
            ALLOWED_HOSTS = s.ALLOWED_HOSTS
            ah_type = type(ALLOWED_HOSTS)
            ALLOWED_HOSTS = list(ALLOWED_HOSTS)
            domains = utils.get_all_domains(self.configured_data['DOMAINS'])
            for domain in domains:
                if domain not in ALLOWED_HOSTS:
                    ALLOWED_HOSTS.append(domain)
            s.ALLOWED_HOSTS = ah_type(ALLOWED_HOSTS)
        return self.configured_data
