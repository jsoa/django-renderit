#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib

from django.db.models import Model
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template import Context
from django.template.loader import select_template

from ..settings import (
    CONCATINATION_STRING, ROOT_TEMPLATE_PATH, DEBUG, SITE_GET_FUNC,
    SITE_GROUPS)

register = Library()


def generate_type_string(obj, concat=CONCATINATION_STRING):
    """Retreive the type, either a django content type or just the object type.

    """
    type_str = ""
    if isinstance(obj, Model):
        model_name = getattr(obj._meta, 'module_name', getattr(obj._meta, 'model_name'))
        type_str = "%s%s%s" % (obj._meta.app_label, concat, model_name)
    else:
        type_str = obj.__class__.__name__

    return type_str.lower()


def get_site():
    try:
        mod = SITE_GET_FUNC.split('.')[:-1]
        func = SITE_GET_FUNC.split('.')[-1]
        module = importlib.import_module('.'.join(mod))
        return getattr(module, func)()
    except (Exception, ):
        return ''


def default_get_site_func():
    from django.contrib.sites.models import Site
    site = Site.objects.get_current()
    return site.id


def get_group_paths(group):
    # Split the groups by a slash in the event multiple paths were supplied,
    # mske sure its reversed as well.
    split_group = group and group.split('/') or []
    return ['/'.join(g) for g in reversed([
        split_group[:n + 1] for n, a in enumerate(split_group)])]


def generate_template_list(type_string, args=None, prefix=None, group=None,
                           concat=CONCATINATION_STRING,
                           default_tmpl='default',
                           default_tmpl_path=ROOT_TEMPLATE_PATH,
                           site=SITE_GROUPS):
    """Generate a template list using supplied arguments.

    `type_string` - the type of object
    `args` - a list of suffixes append to the `type_string`
    `prefix` - a string that is prefixed to the `type_string`
    `group` - a string of the group, a.k.a. folder
    `concat` - a string used when append the strings together
    `default_tmpl` - the default template name
    `default_tmpl_path` - root path where to look for the generated templates

    """
    args, prefix, group = args or [], prefix or '', group or ''
    template_list = []

    arg_list = list(args)
    # Insert to the object type string to the arg list
    arg_list.insert(0, type_string)
    # Build the default arg list without group or prefix
    argstr_list = [concat.join(arg_list[0:x]) for x in \
                    range(len(arg_list), 0, -1)]

    # Using the arg_str_list apply the prefix (if one is supplied)
    prefix_list = ['%s%s%s' % (prefix, concat, x) for x in \
                   argstr_list if prefix]

    # Add the site to the group, if possible
    site_group = None
    # If site is None, use settings to determine if we sould use site groups
    # Supplied site var takes priority
    if site:
        site_group = '{}{}{}'.format(get_site(), group and '/' or '', group)

    # Generate the group paths (with site and without)
    group_paths = []
    group_paths.extend(get_group_paths(site_group))
    group_paths.extend(get_group_paths(group))

    # Start building the template list starting with group, prefix and args,
    # then just group and args.
    for grp in group_paths:
        template_list.extend(['%s/%s' % (grp, x) for x in prefix_list])
        template_list.extend(['%s/%s' % (grp, x) for x in argstr_list])

    # Add the prefixed_list and arg_str_list (without group)
    template_list.extend(prefix_list)
    template_list.extend(argstr_list)

    # Add the default template
    template_list.append(default_tmpl)

    # Rebuild the template list adding the path and extension
    template_list = ['%s/%s.html' % (
        default_tmpl_path, x) for x in template_list]

    if DEBUG:
        print('RENDERIT-DEBUG - Template List: {}'.format(template_list))

    return template_list


def resolve_variable(value, context, none_on_fail=False):
    """A wrapper function to resolve template variables.

    Will return None if [none_on_fail] is [True], otherwise
    it will return [value]

    """
    try:
        return Variable(value).resolve(context)
    except Exception:
        if none_on_fail:
            return None
        return value


class RenderItNode(Node):
    def __init__(self, obj, path_args, kwargs, varname):
        self.obj = obj
        self.path_args = path_args
        self.kwargs = kwargs
        self.varname = varname

    def render(self, context):
        # resolve the only required argument, obj
        obj = resolve_variable(self.obj, context)

        kwargs = self.kwargs.copy()

        # Resolve the extra kwargs
        with_context = resolve_variable(kwargs.pop('context', False), context)
        group = resolve_variable(kwargs.pop('group', None), context)
        prefix = resolve_variable(kwargs.pop('prefix', None), context)
        concat = resolve_variable(
            kwargs.pop('concat', CONCATINATION_STRING), context)
        with_site = resolve_variable(kwargs.pop('site', None), context)

        path_args = []
        extra_context = {}

        for arg in self.path_args:
            path_args.append(resolve_variable(arg, context))

        if isinstance(with_context, (str, )):
            with_context = with_context.lower() == 'true' and True or False

        if with_context:
            extra_context = context
        else:
            extra_context = context.new({})

        # Render the object
        rendered = render_obj(
            obj, path_args, group, prefix, concat, with_site, extra_context)

        # Store the rendered object in the context if varname was supplied
        if self.varname:
            context[self.varname] = rendered
            return ''

        return rendered


def do_renderit(parser, token):
    """
        {% renderit obj [arg] [arg] .. [with] [group=G] [prefix=P] [concat=C] [context=True|False] [site=True|False|None] [as] [varname] %}

        {% renderit myobj myvar with group=myobj.category prefix=custom context=True site=False %}
    """
    argv = token.contents.split()
    argc = len(argv)

    if argc < 1:
        raise TemplateSyntaxError(
            '%s tag requires at least one argument' % argv[0])

    # first item is the object to be rendered
    obj = argv[1]

    # get the index of 'as' or the total length of the arguments
    a = 'as' in argv and argv.index('as') or len(argv)
    # get the index from 'with' to 'as' or the total length of arguments
    e = 'with' in argv and argv.index('with') or a

    # the path args are from the object to either 'with', 'as' or
    # length of arguments
    path_args = argv[2: e]
    # kwargs are from 'with' to 'as' or to length of arguments
    kwargs = argv[e + 1: a]
    # the varname is the last element of the list if 'as' is present
    varname = argv[a:] and argv[a + 1] or None

    # split the kargs by '=' and make a doct
    kwargs = dict([(x.split("=")[0], x.split("=")[1]) for x in \
                   kwargs if '=' in x])

    return RenderItNode(obj, path_args, kwargs, varname)

register.tag("renderit", do_renderit)


def render_obj(obj, args, group, prefix, concat, site, context):
    """
    Render the content
    """
    type_str = generate_type_string(obj, concat)

    # Generate the template list
    template_list = generate_template_list(
        type_str, args, prefix, group, concat=concat, site=site)

    # Select the template
    tmpl = select_template(template_list)
    if not tmpl:
        return None

    # Add the context
    ret_context = Context()
    ret_context.update(context)
    ret_context.update({'obj': obj})

    # return the rendered content
    return tmpl.render(ret_context)
