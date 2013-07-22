from django.conf.urls.defaults import patterns, url


from django.views.generic.simple import direct_to_template
from django.contrib.auth.models import User

from example.sample_app.models import get_or_create_example

main_user = User.objects.all()[0]

int_value = 231
float_value = 112.232

string_value = "this is something"

unicode_value = u"This is something else"

class c(object):
    var1 = 123
    var2 = "custom"

context = {'main_user': main_user,
           'int_value': int_value,
           'float_value': float_value,
           'string_value': string_value,
           'unicode_value': unicode_value,
           'custom_class': c}

context.update(get_or_create_example())

urlpatterns = patterns('',
    url(r'^$',
        direct_to_template,
        {'template': 'index.html',
         'extra_context': context}),
)
