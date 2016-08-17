.. _settings:

========
Settings
========

All settings are grouped in the `RENDERIT_SETTINGS` dictionary, below are all the possible options

.. note::

   You can also use individual settings by prepending `RENDERIT_` in front of the names below.
   If you combine both, the individual settings will act as defaults, and the dictionary
   will override the setting if supplied

.. _setting_concatination_string:

CONCATINATION_STRING
====================

Change the default concatination strings, default is _ (underscore)

.. _root_template_path:

ROOT_TEMPLATE_PATH
==================

Change the default root template path to look for the templates, default is
**/renderit/**

.. _debug:

DEBUG
=====

Outputs some debugging information to the console, defaults to the value of `DEBUG`

.. _site_groups:

SITE_GROUPS
===========

Boolean value indicated if renderit should care about `sites`

.. _site_get_func:

SITE_GET_FUNC
=============

By default when site groups are enabled, it will use the `pk` of the site. However
if we want cleaner names, you can define your own function to get the value.
Defaults to `renderit.templatetags.renderit_tags.default_get_site_func`
