
.. _templatetags:

=============
Template Tags
=============

.. contents::
   :depth: 3

renderit
========

Syntax
------
.. code-block:: django

    {% renderit [object] [arg] [arg] ... [with] [group=S] [prefix=S] [concat=S] [context=True|False] [as] [varname] %} 
    
Examples
--------

**Simplest Form**:

.. code-block:: django

    {% renderit request.user %}
    
**Multiple Arguments**:

.. code-block:: django

    {% renderit request.user auth custom %}
    
**With Prefix**

.. code-block:: django

    {% renderit request.user auth custom with prefix=header %}
    
**Change concatination string to be __ (double under score)**

.. code-block:: django

    {% renderit request.user auth custom with prefix=header concat="__" %}
    
arguments
---------

object
^^^^^^

Only required argument, can be any python object.

args
^^^^

Anything specified after [object] and before [with] will be treated as extra 
concatination strings. These can also be context variables.


.. note::

    If an object is resolved and contains a space, the argument will be 
    slugified, using ``django.template.defaultfilters.slugify``
    
with
^^^^

Required only if [group], [prefix] or [concat] is used.

group
^^^^^

This value is used to better structure the template location. A folder with 
the supplied value will be preprened to template path.

**Example**

.. code-block:: django

    {% renderit auth.user with group='users' %}
    
Template path built::

    '/renderit/users/auth_user.html'

prefix
^^^^^^

Prefixes the template with supplied value.

**Example**

.. code-block:: django

    {% renderit auth.user with prefix='users' %}
    
Template path built::

    '/renderit/users_auth_user.html'

concat
^^^^^^

Change the default concatination string when building templates, default is 
_ (underscore)

**Example**

.. code-block:: django

    {% renderit auth.user with concat="__" %}
    
Template path built::

    '/renderit/auth__users.html'

.. note::

    The default concatination string can be changed using 
    :ref:`setting_concatination_string`

context
^^^^^^^

If True (default) the template context will be passed into the template.

as
^^

Only required if a return variable is used.

varname
^^^^^^^

Store the rendered template into a context varaible.

**Example**

.. code-block:: django

    {% renderit auth.user as auth_var %}
    
    {{ auth_var }}
    


