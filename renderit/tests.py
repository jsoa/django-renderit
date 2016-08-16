#!/usr/bin/env python
# -*- coding: utf-8 -*-f
import six

from django.template import Template, Context
from django.test import TestCase

from renderit.templatetags.renderit_tags import generate_template_list
from renderit.templatetags.renderit_tags import generate_type_string


def render(src, ctx=None):
    ctx = ctx or {}
    return Template(src).render(Context(ctx))


class RenderitTests(TestCase):

    fixtures = ['test_data']

    def setUp(self):
        from sample_app.models import DummyEntry
        self.entry = DummyEntry.objects.get(pk=1)

    def test_default_template_tag(self):
        tmpl = '{% load renderit_tags %}'\
               '{% renderit obj %}'
        self.assertEqual(
            render(tmpl, {}), '{ RENDERIT DEFAULT TEMPLATE }')

    def test_template_tag(self):
        tmpl = '{% load renderit_tags %}'\
               '{% renderit entry %}'

        ctx = {'entry': self.entry, 'other': 'string'}

        self.assertEqual(
            render(tmpl, ctx),
            '{ CONTENT SPECIFIC } Sample Entry #1 (ENTRY)\n')

    def test_full_template_tag(self):
        tmpl = '{% load renderit_tags %}'\
               '{% renderit entry a b c with group=grp prefix=pre site=False %}'
        self.assertEqual(
            render(tmpl, {'entry': self.entry}),
            '{ CONTENT SPECIFIC } FULL')

    def test_template_tag_with_context(self):
        ctx = {'entry': self.entry, 'other': 'string'}
        # Allow all the context to flow into the renderit template
        tmpl = '{% load renderit_tags %}'\
               '{% renderit entry context with context=True %}'\
               '\nOUTER CONTEXT: {{ other }}'

        self.assertEqual(
            render(tmpl, ctx),
            '{ CONTENT SPECIFIC } (ENTRY) Sample Entry #1'\
            '\nINNER CONTEXT: string'\
            '\nOUTER CONTEXT: string')

    def test_template_tag_with_site(self):
        ctx = {'entry': self.entry}
        tmpl = '{% load renderit_tags %}'\
               '{% renderit entry with site=True %}'
        self.assertEqual(
            render(tmpl, ctx),
            '{ SITE SPECIFIC } (ENTRY) Sample Entry #1\n')


class RenderitTemplateTests(TestCase):
    fixtures = ['test_data']

    maxDiff = None

    def setUp(self):
        from sample_app.models import DummyEntry
        self.entry = DummyEntry.objects.get(pk=1)

    def test_generate_template_defaults(self):
        # The most basic template list
        test = generate_template_list('test')
        self.assertEquals(test, ['renderit/test.html', 'renderit/default.html'])

        # Changes to the default template
        tmpl = generate_template_list('test', default_tmpl='mydefault')
        self.assertEquals(tmpl, ['renderit/test.html', 'renderit/mydefault.html'])

        # Changes to the default template path
        root = generate_template_list('test', default_tmpl_path='myroot')
        self.assertEquals(root, ['myroot/test.html', 'myroot/default.html'])

    def test_generate_templates_concat(self):
        concat = generate_template_list('test', args=['1', '2'], concat='__')
        self.assertEquals(concat, [
            'renderit/test__1__2.html',
            'renderit/test__1.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_type_string(self):
        from sample_app.models import DummyVideo, DummyImage

        class X(object):
            pass

        types = {
            'str': 'str',
            'dict': {'key': 'val'},
            'list': ['1', 2],
            'tuple': (1, 2),
            'set': set(['set']),
            'bool': True,
            'int': 1,
            'float': 1.1,
            'nonetype': None,
            'complex': 1.0j,
            'generator': (x for x in range(2)),
            'x': X(),
            'type': X,
            'sample_app_dummyvideo': DummyVideo(),
            'sample_app_dummyimage': DummyImage(),
            'modelbase': DummyVideo,
        }

        if six.PY2:
            types.update({'unicode': u'unicode'})

        for ty, va in types.items():
            uc = generate_type_string(va)
            self.assertEquals(uc, ty)

    def test_generate_templates_type(self):
        from django.contrib.contenttypes.models import ContentType
        ctype = ContentType.objects.get_for_model(self.entry)
        type_string = '{0}{1}{2}'.format(ctype.app_label.lower(), '_', ctype.model.lower())
        a = generate_template_list(type_string)
        self.assertEquals(a, [
            'renderit/sample_app_dummyentry.html',
            'renderit/default.html'])

    def test_generate_template_args(self):
        args = generate_template_list('test', args=['1', '2'])
        self.assertEquals(args, [
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_template_prefix(self):
        prefix = generate_template_list('test', prefix='pre')
        self.assertEquals(prefix, [
            'renderit/pre_test.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_template_group(self):
        group = generate_template_list('test', group='grp')
        self.assertEquals(group, [
            'renderit/grp/test.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_template_arg_prefix(self):
        args_prefix = generate_template_list('test', args=['1', '2'], prefix='pre')
        self.assertEquals(args_prefix, [
            'renderit/pre_test_1_2.html',
            'renderit/pre_test_1.html',
            'renderit/pre_test.html',
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_template_arg_group(self):
        args_prefix = generate_template_list('test', args=['1', '2'], group='grp')
        self.assertEquals(args_prefix, [
            'renderit/grp/test_1_2.html',
            'renderit/grp/test_1.html',
            'renderit/grp/test.html',
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',
            'renderit/default.html'])

    def test_generate_template_arg_prefix_group(self):
        args_prefix_group = generate_template_list(
            'test', args=['1', '2'], prefix='pre', group='grp')
        self.assertEquals(args_prefix_group, [
            'renderit/grp/pre_test_1_2.html',
            'renderit/grp/pre_test_1.html',
            'renderit/grp/pre_test.html',
            'renderit/grp/test_1_2.html',
            'renderit/grp/test_1.html',
            'renderit/grp/test.html',

            'renderit/pre_test_1_2.html',
            'renderit/pre_test_1.html',
            'renderit/pre_test.html',
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',

            'renderit/default.html'])

    def test_generate_template_groups(self):
        groups = generate_template_list(
            'test', group='a/b')

        self.assertEquals(groups, [
            'renderit/a/b/test.html',
            'renderit/a/test.html',
            'renderit/test.html',
            'renderit/default.html'
        ])

    def test_generate_template_sites(self):
        groups = generate_template_list(
            'test', site=True
            )

        self.assertEquals(groups, [
            'renderit/1/test.html',
            'renderit/test.html',
            'renderit/default.html'
        ])

        groups = generate_template_list(
            'test', group='a/b', site=True
            )

        self.assertEquals(groups, [
            'renderit/1/a/b/test.html',
            'renderit/1/a/test.html',
            'renderit/1/test.html',
            'renderit/a/b/test.html',
            'renderit/a/test.html',
            'renderit/test.html',
            'renderit/default.html'
            ])

    def test_generate_template_args_group(self):
        groups = generate_template_list(
            'test', args=['1', '2'], group='a/b')

        self.assertEquals(groups, [
            'renderit/a/b/test_1_2.html',
            'renderit/a/b/test_1.html',
            'renderit/a/b/test.html',

            'renderit/a/test_1_2.html',
            'renderit/a/test_1.html',
            'renderit/a/test.html',

            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',

            'renderit/default.html'
        ])

    def test_generate_template_args_prefix_group(self):
        groups = generate_template_list(
            'test', args=['1', '2'], prefix='pre', group='a/b')

        self.assertEquals(groups, [
            'renderit/a/b/pre_test_1_2.html',
            'renderit/a/b/pre_test_1.html',
            'renderit/a/b/pre_test.html',
            'renderit/a/b/test_1_2.html',
            'renderit/a/b/test_1.html',
            'renderit/a/b/test.html',

            'renderit/a/pre_test_1_2.html',
            'renderit/a/pre_test_1.html',
            'renderit/a/pre_test.html',
            'renderit/a/test_1_2.html',
            'renderit/a/test_1.html',
            'renderit/a/test.html',

            'renderit/pre_test_1_2.html',
            'renderit/pre_test_1.html',
            'renderit/pre_test.html',
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',

            'renderit/default.html'
        ])

    def test_generate_template_args_prefix_group_site(self):
        groups = generate_template_list(
            'test', args=['1', '2'], prefix='pre', group='a/b', site=True)

        self.assertEquals(groups, [
            'renderit/1/a/b/pre_test_1_2.html',
            'renderit/1/a/b/pre_test_1.html',
            'renderit/1/a/b/pre_test.html',
            'renderit/1/a/b/test_1_2.html',
            'renderit/1/a/b/test_1.html',
            'renderit/1/a/b/test.html',

            'renderit/1/a/pre_test_1_2.html',
            'renderit/1/a/pre_test_1.html',
            'renderit/1/a/pre_test.html',
            'renderit/1/a/test_1_2.html',
            'renderit/1/a/test_1.html',
            'renderit/1/a/test.html',

            'renderit/1/pre_test_1_2.html',
            'renderit/1/pre_test_1.html',
            'renderit/1/pre_test.html',
            'renderit/1/test_1_2.html',
            'renderit/1/test_1.html',
            'renderit/1/test.html',

            'renderit/a/b/pre_test_1_2.html',
            'renderit/a/b/pre_test_1.html',
            'renderit/a/b/pre_test.html',
            'renderit/a/b/test_1_2.html',
            'renderit/a/b/test_1.html',
            'renderit/a/b/test.html',

            'renderit/a/pre_test_1_2.html',
            'renderit/a/pre_test_1.html',
            'renderit/a/pre_test.html',
            'renderit/a/test_1_2.html',
            'renderit/a/test_1.html',
            'renderit/a/test.html',

            'renderit/pre_test_1_2.html',
            'renderit/pre_test_1.html',
            'renderit/pre_test.html',
            'renderit/test_1_2.html',
            'renderit/test_1.html',
            'renderit/test.html',

            'renderit/default.html'
            ])
