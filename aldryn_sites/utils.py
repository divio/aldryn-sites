# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from django.contrib.sites.models import Site
import yurl


# global variable so we don't do this too often.
# I wish there were an "application ready" signal.
_has_set_site_names = False


def set_site_names(force=False):
    global _has_set_site_names
    if _has_set_site_names and not force:
        return

    _has_set_site_names = True
    sites = {site.id: site for site in Site.objects.all()}
    for site_id, site_config in settings.ALDRYN_SITES_DOMAINS.items():
        if site_id not in sites.keys():
            sites[site_id] = Site.objects.create(id=site_id)
        site = sites[site_id]
        if not site.name == site_config['domain']:
            site.domain = site_config['domain']
            site.save()


def get_redirect_url(current_url, config, https=False):
    """
    :param current_url: the url that is being called
    :param config: redirect configuration for this url
    :param want_https: whether redircts should go to https
    :return: None for no redirect or an url to redirect to
    """
    primary_domain = config['domain']
    domains = set(config.get('aliases', [])) | set((primary_domain,))
    redirect_domains = set(config.get('redirects', []))
    url = yurl.URL(current_url)
    target_proto = 'https' if https else 'http'
    redirect_url = None
    if url.host in domains and url.scheme == target_proto:
        return
    if url.is_host_ip() or url.is_host_ipv4():
        return
    if url.host in domains and url.scheme != target_proto:
        redirect_url = url.replace(scheme=target_proto)
    elif '*' in redirect_domains or url.host in redirect_domains:
        redirect_url = url.replace(scheme=target_proto, host=primary_domain)
    if redirect_url:
        return '{}'.format(redirect_url)
