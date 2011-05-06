from django.conf import settings

RENDERIT_SETTINGS = getattr(settings, 'RENDERIT_SETTINGS', {
    'CONCATINATION_STRING': getattr(settings, 'RENDERIT_CONCATINATION_STRING', '_'), 
    'ROOT_TEMPLATE_PATH': getattr(settings, 'RENDERIT_ROOT_TEMPLATE_PATH', 'renderit'),
})

globals().update(RENDERIT_SETTINGS)
