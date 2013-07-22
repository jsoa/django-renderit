#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models import Model
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template import Context
from django.template.loader import select_template

register = Library()

from ..settings import CONCATINATION_STRING, ROOT_TEMPLATE_PATH


def generate_type_string(obj, concat=CONCATINATION_STRING):
    """Retreive the type, either a django content type or just the object type.

    """
    type_str = ""
    if isinstance(obj, Model):
        type_str = "%s%s%s" % (
            obj._meta.app_label, concat, obj._meta.module_name)
    else:
        type_str = obj.__class__.__name__

    return type_str.lower()


def generate_template_list(type_string, args=None, prefix=None, group=None,
                           concat=CONCATINATION_STRING,
                           default_tmpl='default',
                           default_tmpl_path=ROOT_TEMPLATE_PATH):
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

    # Start building the template list starting with group, prefix and args,
    # then just group and args.
    template_list.extend(['%s/%s' % (group, x) for x in prefix_list if group])
    template_list.extend(['%s/%s' % (group, x) for x in argstr_list if group])

    # Add the prefixed_list and arg_str_list (without group)
    template_list.extend(prefix_list)
    template_list.extend(argstr_list)

    # Add the default template
    template_list.append(default_tmpl)

    # Rebuild the template list adding the path and extension
    template_list = ['%s/%s.html' % (
        default_tmpl_path, x) for x in template_list]

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
    def __init__(self, obj, path_args, extra_kwgs, varname):
        self.obj = obj
        self.path_args = path_args
        self.extra_kwgs = extra_kwgs
        self.varname = varname

    def render(self, context):

        # resolve the only required argument, obj
        obj = resolve_variable(self.obj, context)
        path_args = []
        extra_kwgs = {}
        for arg in self.path_args:
            path_args.append(resolve_variable(arg, context))

        for k, v in self.extra_kwgs.items():
            if k == 'context':
                if v.lower() == True:
                    extra_context = {}
                    extra_kwgs[k] = True
                    extra_context.update(context.__dict__)
                    extra_kwgs['extra_context'] = extra_context
                else:
                    extra_kwgs[k] = False

                continue
            extra_kwgs[k] = resolve_variable(v, context)

        v = render_obj(obj, *path_args, **extra_kwgs)
        if self.varname:
            context[self.varname] = v
            return ""
        return v


def do_renderit(parser, token):
    """
        {% renderit obj [arg] [arg] .. [with] [group=G] [prefix=P] [concat=C] [context=True|False] [as] [varname] %}

        {% renderit myobj myvar with group=myobj.category prefix=custom context=True %}
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
    # extra args are from 'with' to 'as' or to length of arguments
    extra_args = argv[e + 1: a]
    # the varname is the last element of the list if 'as' is present
    varname = argv[a:] and argv[a + 1] or None

    # split the extra args by '=' and make a doct
    extra_kwgs = dict([(x.split("=")[0], x.split("=")[1]) for x in \
                       extra_args if '=' in x])

    return RenderItNode(obj, path_args, extra_kwgs, varname)

register.tag("renderit", do_renderit)


def render_obj(obj, *args, **kwargs):
    """
    Render the content
    """
    prefix = kwargs.pop("prefix", None)
    group = kwargs.pop("group", None)
    concat = kwargs.pop("concat", CONCATINATION_STRING)
    context = kwargs.pop("context", False)
    extra_context = kwargs.pop("extra_context", {})

    type_str = generate_type_string(obj, concat)

    # Generate the template list
    template_list = generate_template_list(
        type_str, args, prefix, group, concat=concat)

    # Select the template
    tmpl = select_template(template_list)
    if not tmpl:
        return None

    # Add the context
    ret_context = Context()
    ret_context.update({'obj': obj})
    if context:
        ret_context.update(extra_context)

    # return the rendered content
    return tmpl.render(ret_context)
