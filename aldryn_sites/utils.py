# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import re
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
        config_name = site_config.get('name', None)
        config_domain = site_config['domain']

        if site_id not in sites.keys():
            sites[site_id] = Site.objects.create(
                id=site_id,
                name=config_name or config_domain,
                domain=config_domain,
            )
        else:
            site = sites[site_id]
            if site.domain != config_domain:
                # domain needs to be updated
                site.domain = config_domain
                site.save()


def get_redirect_url(current_url, config, https=None):
    """
    priorities are (primary domain and aliases are treated the same):
        exact redirect match > exact alias match > pattern redirect match > pattern alias match
    :param current_url: the url that is being called
    :param config: redirect configuration for this url
    :param want_https: whether redirects should go to https (None keeps the current scheme)
    :return: None for no redirect or an url to redirect to
    """
    primary_domain = config['domain']
    domains = set(config.get('aliases', [])) | set((primary_domain,))
    domain_patterns = compile_regexes(domains)
    redirect_domains = set(config.get('redirects', []))
    redirect_domain_patterns = compile_regexes(redirect_domains)
    url = yurl.URL(current_url)
    if https is None:
        target_scheme = url.scheme
    else:
        target_scheme = 'https' if https else 'http'
    redirect_url = None
    if url.is_host_ip() or url.is_host_ipv4():
        # don't redirect for ips
        return
    if url.host in domains and url.scheme == target_scheme:
        # exact host and scheme match: Nothing to do
        return
    if url.host in domains and url.scheme != target_scheme:
        # exact alias match, but scheme mismatch: redirect to changed scheme
        redirect_url = url.replace(scheme=target_scheme)
    elif url.host in redirect_domains:
        # exact redirect match: redirect
        redirect_url = url.replace(scheme=target_scheme, host=primary_domain)
    elif url.host in domains:
        # exact alias match: nothing to do
        return
    elif match_any(redirect_domain_patterns, url.host):
        # pattern redirect match: redirect
        redirect_url = url.replace(scheme=target_scheme, host=primary_domain)
    elif match_any(domain_patterns, url.host):
        # pattern alias match
        if url.scheme != target_scheme:
            # pattern alias match and scheme mismatch: redirect
            redirect_url = url.replace(scheme=target_scheme)
        else:
            return

    if redirect_url:
        return '{}'.format(redirect_url)


def get_all_domains(config):
    domains = []
    for site in config.values():
        domains.append(site['domain'])
        for domain in site.get('aliases', []):
            domains.append(domain)
        for domain in site.get('redirects', []):
            domains.append(domain)
    return domains


def compile_regexes(pattern_strings):
    return [
        (re.compile(pattern_string) if not hasattr(pattern_string, 'match') else pattern_string)
        for pattern_string in pattern_strings
    ]


def match_any(patterns, string):
    for pattern in patterns:
        if pattern == string:
            # not a regex, but an exact match
            return True
        if hasattr(pattern, 'pattern') and pattern.pattern == string:
            # it's a regex, but the pattern matches 1-to-1 (no regex rules inside)
            return True
        if hasattr(pattern, 'match') and pattern.match(string):
            return True
    return False
