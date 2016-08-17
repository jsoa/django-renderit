.. _templatefallback:

=================
Template Fallback
=================

.. contents::
   :depth: 3

Fallback template paths are generated based on the arguments supplied. A list
templates is created and then ``select_template`` is called on the list.

Simple Example
==============

.. code-block:: django

    {% renderit auth.user %}

Generated List::

    ['/renderit/auth_user.html',
     '/renderit/default.html']


.. note::

    The default template root path can be changed via :ref:`root_template_path`


Arguments Example
=================


Single Argument
---------------

.. code-block:: django

    {% renderit auth.user auth %}

Generated list::

    ['/renderit/auth_user_auth.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']

Mulitple Arguments
------------------

.. code-block:: django

    {% renderit auth.user auth homepage %}

Generated list::

    ['/renderit/auth_user_auth_homepage.html',
     '/renderit/auth_user_auth.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']

Prefix
------

Suppling a prefix will gerernate two sets of templates, one set with the prefix
and one set without the prefix

.. code-block:: django

    {% renderit auth.user with prefix=userinfo %}

Generated List::

    ['/renderit/userinfo_auth_user.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']

**With Arguments**

.. code-block:: django

    {% renderit auth.user homepage custom with prefix=userinfo %}

Generated List::

    ['/renderit/userinfo_auth_user_homapage_custom.html',
     '/renderit/userinfo_auth_user_homepage.html',
     '/renderit/userinfo_auth_user.html',

     '/renderit/auth_user_homepage_custom.html',
     '/renderit/auth_user_homapage.html',
     '/renderit/auth_user.html',

     '/renderit/default.html']

Group
-----

*Changed in version `1.1`*

Group will append the string and act like a directory rather then a extra
template path string.

.. code-block:: django

    {% renderit auth.user with group=users %}

Generated List::

    ['/renderit/users/auth_user.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']


The group argument can also be a path i.e. `users/homepage`

*New in version `1.1`*

.. code-block:: django

    {% renderit auth.user with group=users/homepage %}

Generated List::

    ['/renderit/users/homepage/auth_user.html',
     '/renderit/users/auth_user.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']


Site
----

*New in version `1.2`*

We can group templates by the current `site`. This option can be supplied
via the template tag as `site=True` or enabled globally using the `SITE_GROUPS`
setting.

.. code-block:: django

    {% renderit auth.user with site=True %}

Generated List::

    ['/renderit/1/auth_user.html',
     '/renderit/auth_user.html',
     '/renderit/default.html']

The example above will automatically apply the site id as part of the group.

.. note::

   While this looks like just another group i.e. `1/a/b`, it acts slightly
   different when the `site` is reached. Normally when the last group is
   reached, in this case `1` the template generator would just remove the `1`
   and try any `prefix` and `arg` combination left, but the site functionality
   will remove the `1` and then try all the normal groups (anything other than
   the site) all over again.

Here is an example without sites::

.. code-bloack:: django

    {% renderit test with groups=1/a/b %}

Generated List::

  ['renderit/1/a/b/test.html',

   'renderit/1/a/test.html',

   'renderit/1/test.html',

   'renderit/test.html',

   'renderit/default.html']

Here is an example with sites (notice the removal of `1` in the groups)::

.. code-bloack:: django

    {% renderit test with groups=a/b sites=True %}

Generated List::

  ['renderit/1/a/b/test.html',

  'renderit/1/a/test.html',

  'renderit/1/test.html',

  'renderit/a/b/test.html',

  'renderit/a/test.html',

  'renderit/testhtml',

  'renderit/default.html']

As shown, the site id is used first, but when the site id is removed, it
will reset the groups with no site id. This gives us the ability to have
defaults and site overrides.

Site value generation
^^^^^^^^^^^^^^^^^^^^^

The above examples showed the default value used, the `pk` of the site,
but this isn't very developer friendly. When `site` ability is enabled
we can specify a custom site value function which should yield a string.
The default is `renderit.templatetags.renderit_tags.default_get_site_func`

Change the setting `SITE_GET_FUNC` to a custom function to return something
more friendly. For example:

.. code-block:: python

    RENDERIT_SETTINGS = {
         'SITE_GET_FUNC': 'example.sample_app.utils.get_site_name'
    }

.. code-block:: python

    def get_site_name():
        site_map = {
           1: 'white',
           2: 'black',
           3: 'red',
           4: 'blue'
        }
        return site_map.get(Site.objects.get_current().pk)


Combined
--------

The list of generated template paths can get rather large when using multiple
arguments, a prefix and a group together

.. code-block:: django

    {% renderit auth.user hompage custom with prefix=logininfo group=users %}

Generated List::

    ['/renderit/users/logininfo_auth_user_admins_custom.html',
     '/renderit/users/logininfo_auth_user_admin.html',
     '/renderit/users/logininfo_auth_user.html',

     '/renderit/users/logininfo_auth_user_admin_custom.html',
     '/renderit/users/logininfo_auth_user_homepage.html',
     '/renderit/users/auth_user.html',

     '/renderit/logininfo_auth_user_homepage_custom.html',
     '/renderit/logininfo_auth_user_homepage.html',
     '/renderit/logininfo_auth_user.html',

     '/renderit/auth_user_homepage_custom.html',
     '/renderit/auth_user_homepage.html',
     '/renderit/auth_user.html',

     '/renderit/default.html']

What we have here is 2 sets with 2 inner sets of templates, one set has the
group **users** one without, the inner set has one set with
prefix **logininfo** and one set without.

.. note::

    This is just the generated template path list, these templates do not have
    to exist, this is simply a way to fallback to other templates in case a
    template does not exist.


With the update to `group` argument to allow a path, the generate list gets
even larger.

.. code-block:: django

    {% renderit auth.user admins custom with prefix=logininfo group=users/homepage %}

Generated List::


    ['/renderit/users/homepage/logininfo_auth_user_admins_custom.html',
     '/renderit/users/homepage/logininfo_auth_user_admins.html',
     '/renderit/users/homepage/logininfo_auth_user.html',

     '/renderit/users/homepage/auth_user_admins_custom.html',
     '/renderit/users/homepage/auth_user_admins.html',
     '/renderit/users/homepage/auth_user.html',

     '/renderit/users/logininfo_auth_user_admins_custom.html',
     '/renderit/users/logininfo_auth_user_admins.html',
     '/renderit/users/logininfo_auth_user.html',

     '/renderit/users/auth_user_admins_custom.html',
     '/renderit/users/auth_user_admins.html',
     '/renderit/users/auth_user.html',

     '/renderit/logininfo_auth_user_admins_custom.html',
     '/renderit/logininfo_auth_user_admins.html',
     '/renderit/logininfo_auth_user.html',

     '/renderit/auth_user_admins_custom.html',
     '/renderit/auth_user_admins.html',
     '/renderit/auth_user.html',

     '/renderit/default.html']

This is similar to the previous example, except that now we have `users/homepage`
as one set and `users` as another set



The other arguments
===================

concat
------

This argumennt is taken literally and will not create any extra sets. If we
take the last example and add concatination string to be __ (double underscore)
we would get:

.. code-block:: django

    {% renderit auth.user hompage custom with prefix=logininfo group=users concat="__" %}

Generated List::

    ['/renderit/users/logininfo__auth__user__homepage__custom.html',
     '/renderit/users/logininfo__auth__user__homepage.html',
     '/renderit/users/logininfo__auth__user.html',

     '/renderit/users/auth__user__homepage__custom.html',
     '/renderit/users/auth__user__homepage.html',
     '/renderit/users/auth__user.html',

     '/renderit/logininfo__auth__user__homepage__custom.html',
     '/renderit/logininfo__auth__user__homepage.html',
     '/renderit/logininfo__auth__user.html',

     '/renderit/auth__user__homepage__custom.html',
     '/renderit/auth__user__homepage.html',
     '/renderit/auth__user.html',

     '/renderit/default.html']
