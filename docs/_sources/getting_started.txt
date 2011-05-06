.. _getting_started:

===============
Getting Started
===============

The idea here is to take a object and render it based off of its content type.

django-renderit is one template tag called ``renderit`` and it takes 
a bunch of different parameters to determine what template to render.

Basic Usage
===========

.. code-block:: django

	{% load renderit %}
	
	{% renderit object %}
	
This will render ``object`` using the default template, which is::

    '/renderit/default.html'

You can then create a template that is object specific, for example, if the 
object is a``auth.user`` instance, it will look for this template::
  
    '/renderit/auth_user.html'

Extra Arguments
===============

We can add extra arguments to further make this template unique, for example, 
lets say we want to render the authentication information for websites that 
required logged in users. We would normally have some html on our base 
template, such as

.. code-block:: django

    <html>
        <head>MySite</head>
        <body>
            <div class="auth">
                Welcome, 
                {% if request.user.is_authenticated %}
                    {{ request.user.username }}, <a href="/profile/">Profile</a> <a href="/logout/">Logout</a>
                {% else %}
                    Guest, <a href="/login/">Login</a> or <a href="/register/">Register</a>
                {% endif %}
            </div>
            <div class="content">
                ...
            </div>
        </body>
    </html>
    
``renderit``'s goal is to take these little blocks of code and seperate them out 
in there own specific, resuable templates, and to clean up the main templates.

.. code-block:: django

    {% load renderit %}
    <html>
        <head>MySite</head>
        <body>
            {% renderit request.user auth %}
            <div class="content">
                ...
            </div>
        </body>
    </html>
    
The above example takes an extra argument ``auth``, this can be a context 
variable or taken literally. If ``auth`` not a variable in the template then 
``renderit`` will take is as a string::

    '/renderit/auth_user_auth.html'
  
Any arguments specified after the object, will be appended to the end of the 
template name.

While the above example can be used with django's include tag in the same way, 
a better use case would be when your dealing with a list of gerneric objects.

Lets take the following models::

    class DummyEntry(models.Model):
        title = models.CharField(max_length=200)
        body = models.TextField()
        publish_date = models.DateTimeField(default=datetime.datetime.now)
        author = models.CharField(max_length=200)
        
        def __unicode__(self):
            return self.title
            
        
    class DummyBookmark(models.Model):
        url = models.URLField()
        name = models.CharField(max_length=200)
        
        
    class DummyVideo(models.Model):
        url = models.URLField()
        name = models.CharField(max_length=200)
        
        
    class DummyImage(models.Model):
        url = models.URLField()
        name = models.CharField(max_length=200)
        
    
    class RelatedContent(models.Model):
        entry = models.ForeignKey(DummyEntry)
        content_type = models.ForeignKey(ContentType)
        object_id = models.IntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        add_date = models.DateTimeField(default=datetime.datetime.now)
    
Lets create and add the content to a generic list::
    
    bm_ctype = ContentType.objects.get_for_model(DummyBookmark)
    vi_ctype = ContentType.objects.get_for_model(DummyVideo)
    im_ctype = ContentType.objects.get_for_model(DummyImage)
    en_ctype = ContentType.objects.get_for_model(DummyEntry)

    
    entry = DummyEntry.objects.create(
        title="This is an example entry",
        body="This is only an example entry",
        author="John Smith")
        
    bm = DummyBookmark.objects.create(
        url="http://google.com",
        name="Google")
           
    vid = DummyVideo.objects.create(
        url="http://www.youtube.com/watch?v=K24mFGlJij0&playnext=1&list=PL4A64BDBA5F9629AE",
        name="Django's Caravan - Gypsy Jazz Guitar - Leigh Jackson") 
            
    img1 = DummyImage.objects.create(
        url="http://www.flickr.com/photos/alisonlyons/5678882139/",
        name="Fair Exchange From alison lyons photography")
        
    RelatedContent.objects.create(
        entry=entry,
        content_type=bm_ctype,
        object_id=bm.pk)
        
    RelatedContent.objects.create(
        entry=entry,
        content_type=vi_ctype,
        object_id=vid.pk)
    
    RelatedContent.objects.create(
        entry=entry,
        content_type=im_ctype,
        object_id=img.pk)
    
    RelatedContent.objects.create(
        entry=entry,
        content_type=en_ctype,
        object_id=entry.pk)

    related_objects = RelatedContent.objects.all()
 
When related_content is used in your template, there will be 4 different 
types of objects. If we dont want they all to look the same, for example have 
a image show up for ``DummyImage`` types or embdeded video 
player for ``DummyVideo`` types, the way we can do that is to have a bunch of 
``if`` statements to check the type of object, but thats ugly, and can clutter 
up the template. Enstead ``renderit`` will know the type of object you are 
trying to render and use the appropriete template.

.. code-block:: django

    {% for obj in related_content %}
        {% renderit obj %}
    {% endfor %}
    
When we output the template list that is created for each item in the loop above, 
it will look something like this::

    [u'renderit/sample_app_dummybookmark.html', 'renderit/default.html']
    [u'renderit/sample_app_dummyvideo.html', 'renderit/default.html']
    [u'renderit/sample_app_dummyimage.html', 'renderit/default.html']
    [u'renderit/sample_app_dummyentry.html', 'renderit/default.html']

We can then create the templates and make them custom to the type of object.

Python Objects
==============

While the examples shown are specific to django models, we can pass in any object 
and its type will be used (slugified) to build the template. If we have a python 
dictionary, the template will be::

    '/renderit/dict.html'

Of course this is rather broad, so we should pass in extra arguments to ensure 
its specific to what we use it for

.. code-block:: django

    {% renderit dict_obj top10 %}
    
The template that will be looked for first would be::

    '/renderit/dict_top10.html'
    
Read more about :ref:`templatetags`

Fallback
========

Fallback template paths are generated based on the arguments supplied, which 
the last possbiel template being '/renderit/default.html'. Read more about 
:ref:`templatefallback`
    
