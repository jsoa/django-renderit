#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

DEFAULT_SETTINGS = {
    'CONCATINATION_STRING': getattr(
        settings, 'RENDERIT_CONCATINATION_STRING', '_'),
    'ROOT_TEMPLATE_PATH': getattr(
        settings, 'RENDERIT_ROOT_TEMPLATE_PATH', 'renderit'),
    'DEBUG': getattr(settings, 'RENDERIT_DEBUG', getattr(settings, 'DEBUG', False)),
    'SITE_GROUPS': getattr(settings, 'RENDERIT_SITE_GROUPS', False),
    'SITE_GET_FUNC': getattr(
        settings, 'RENDERIT_SITE_GET_FUNC',
        'renderit.templatetags.renderit_tags.default_get_site_func')
    }

DEFAULT_SETTINGS.update(getattr(settings, 'RENDERIT_SETTINGS', {}))

globals().update(DEFAULT_SETTINGS)
