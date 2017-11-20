try:
    from django.conf.urls.defaults import patterns, url
except (ImportError, ):
    from django.conf.urls import url

from django.views.generic import TemplateView

from django.contrib.auth.models import User

main_user = User.objects.get_or_create(username='test', email='test@test.com')

int_value = 231
float_value = 112.232

string_value = str("this is something")

unicode_value = u"This is something else"


class c(object):
    var1 = 123
    var2 = "custom"



class TestTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = {
            'main_user': main_user,
            'int_value': int_value,
            'float_value': float_value,
            'string_value': string_value,
            'unicode_value': unicode_value,
            'custom_class': c}

        from example.sample_app.models import get_or_create_example
        context.update(get_or_create_example())

        return context

urlpatterns = [
    url(r'^$',
        TestTemplateView.as_view(template_name='index.html'),
    )
]
